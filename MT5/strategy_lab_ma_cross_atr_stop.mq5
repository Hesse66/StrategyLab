#property strict
#property version   "1.00"

#include <Trade/Trade.mqh>

input int      InpFastLen                         = 30;
input int      InpSlowLen                         = 104;
input int      InpAtrLen                          = 70;
input double   InpStopMult                        = 5.1;
input int      InpNoiseLookback                   = 25;
input int      InpMaxNoCross                      = 1;
input bool     InpAllowLong                       = true;
input bool     InpAllowShort                      = true;
input bool     InpBreakevenStopEnabled            = true;
input double   InpBreakevenTriggerMfeR            = 0.25;
input double   InpBreakevenLockR                  = 1.0;
input bool     InpTimeDecayExitEnabled            = true;
input int      InpTimeDecayBars                   = 40;
input double   InpTimeDecayMinMfeR                = 0.35;
input bool     InpHybridTimeDecayTriageEnabled    = true;
input int      InpHybridTimeDecayCheckpoint       = 30;
input double   InpHybridTimeDecayMaxUnrealizedR   = -0.45;
input double   InpHybridTimeDecayMaxMfeR          = 0.15;
input bool     InpHybridReverseExitTriageEnabled  = true;
input double   InpHybridReverseExitMinMfeR        = 0.1;
input bool     InpShortQualityGateEnabled         = true;
input int      InpShortQualityGateLenBars         = 24960;
input bool     InpTimeRiskFilterEnabled           = true;
input string   InpBlockedUtcHoursCsv              = "13,15,21";
input string   InpBlockedPythonWeekdaysCsv        = "6";
input int      InpBrokerUtcOffsetHours            = 0;
input double   InpRiskPct                         = 0.01;
input double   InpMaxLeverage                     = 1.0;
input long     InpMagicNumber                     = 20260501;
input int      InpSlippagePoints                  = 20;
input bool     InpDebugLogging                    = true;

CTrade trade;

datetime g_lastBarTime = 0;
double   g_entryPrice = 0.0;
double   g_initialRisk = 0.0;
double   g_maxFavorableExcursion = 0.0;
double   g_maxAdverseExcursion = 0.0;
datetime g_entryBarTime = 0;
int      g_entryBarsSeen = 0;
int      g_stopStage = 0;

void DebugLog(const string message)
{
   if(InpDebugLogging)
      Print(message);
}

bool CopyRatesSafe(const int count, MqlRates &rates[])
{
   ArraySetAsSeries(rates, true);
   return CopyRates(_Symbol, PERIOD_CURRENT, 0, count, rates) == count;
}

bool NewBarFormed()
{
   MqlRates rates[2];
   if(!CopyRatesSafe(2, rates))
      return false;
   if(rates[0].time == g_lastBarTime)
      return false;
   g_lastBarTime = rates[0].time;
   return true;
}

double NormalizePrice(const double price)
{
   return NormalizeDouble(price, (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS));
}

double MinimumStopDistance()
{
   const double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
   const int stopsLevel = (int)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL);
   const int freezeLevel = (int)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_FREEZE_LEVEL);
   const int requiredLevel = MathMax(stopsLevel, freezeLevel);
   return (requiredLevel + 1) * point;
}

bool IsStopLossValidForPosition(const ENUM_POSITION_TYPE type, const double stopLoss)
{
   if(stopLoss <= 0.0)
      return true;

   const double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   const double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   const double minDistance = MinimumStopDistance();
   if(bid <= 0.0 || ask <= 0.0 || minDistance <= 0.0)
      return false;

   if(type == POSITION_TYPE_BUY)
      return stopLoss < NormalizePrice(bid - minDistance);

   return stopLoss > NormalizePrice(ask + minDistance);
}

int SecondsFromMidnight(const datetime value)
{
   MqlDateTime parts;
   TimeToStruct(value, parts);
   return (parts.hour * 3600) + (parts.min * 60) + parts.sec;
}

bool IsTradeSessionOpenNow()
{
   MqlDateTime nowParts;
   TimeToStruct(TimeCurrent(), nowParts);
   const ENUM_DAY_OF_WEEK day = (ENUM_DAY_OF_WEEK)nowParts.day_of_week;
   const int nowSeconds = (nowParts.hour * 3600) + (nowParts.min * 60) + nowParts.sec;

   datetime fromTime = 0;
   datetime toTime = 0;
   for(uint session = 0; session < 16; ++session)
   {
      if(!SymbolInfoSessionTrade(_Symbol, day, session, fromTime, toTime))
         break;

      const int fromSeconds = SecondsFromMidnight(fromTime);
      const int toSeconds = SecondsFromMidnight(toTime);
      if(fromSeconds == toSeconds)
         return true;
      if(fromSeconds < toSeconds && nowSeconds >= fromSeconds && nowSeconds < toSeconds)
         return true;
      if(fromSeconds > toSeconds && (nowSeconds >= fromSeconds || nowSeconds < toSeconds))
         return true;
   }

   return false;
}

bool ModifyManagedPositionStops(const double stopLoss, const double takeProfit, const string reason)
{
   if(!HasManagedPosition())
      return false;
   if(!IsTradeSessionOpenNow())
      return false;

   const ENUM_POSITION_TYPE type = ManagedPositionType();
   const double normalizedStop = NormalizePrice(stopLoss);
   if(!IsStopLossValidForPosition(type, normalizedStop))
      return false;

   const bool ok = trade.PositionModify(_Symbol, normalizedStop, takeProfit);
   if(!ok)
      DebugLog(StringFormat("%s_MODIFY_FAILED | sl=%.5f | retcode=%d", reason, normalizedStop, trade.ResultRetcode()));
   return ok;
}

double SimpleSmaClose(const MqlRates &rates[], const int shift, const int length, const int total)
{
   if(length <= 0 || shift + length - 1 >= total)
      return EMPTY_VALUE;
   double sum = 0.0;
   for(int i = shift; i < shift + length; ++i)
      sum += rates[i].close;
   return sum / length;
}

double TrueRangeAt(const MqlRates &rates[], const int shift, const int total)
{
   if(shift + 1 >= total)
      return EMPTY_VALUE;
   const double highLow = rates[shift].high - rates[shift].low;
   const double highClose = MathAbs(rates[shift].high - rates[shift + 1].close);
   const double lowClose = MathAbs(rates[shift].low - rates[shift + 1].close);
   return MathMax(highLow, MathMax(highClose, lowClose));
}

double SimpleAtr(const MqlRates &rates[], const int shift, const int length, const int total)
{
   if(length <= 0 || shift + length >= total)
      return EMPTY_VALUE;
   double sum = 0.0;
   for(int i = shift; i < shift + length; ++i)
   {
      const double tr = TrueRangeAt(rates, i, total);
      if(tr == EMPTY_VALUE)
         return EMPTY_VALUE;
      sum += tr;
   }
   return sum / length;
}

bool CsvContainsInt(const string csv, const int needle)
{
   string parts[];
   const int count = StringSplit(csv, ',', parts);
   for(int i = 0; i < count; ++i)
   {
      string item = parts[i];
      StringTrimLeft(item);
      StringTrimRight(item);
      if(item != "" && (int)StringToInteger(item) == needle)
         return true;
   }
   return false;
}

int PythonWeekdayFromMql(const int mqlDayOfWeek)
{
   return (mqlDayOfWeek + 6) % 7;
}

bool IsTimeRiskBlocked(const datetime serverTime)
{
   if(!InpTimeRiskFilterEnabled)
      return false;
   const datetime utcTime = serverTime - (InpBrokerUtcOffsetHours * 3600);
   MqlDateTime parts;
   TimeToStruct(utcTime, parts);
   const int pythonWeekday = PythonWeekdayFromMql(parts.day_of_week);
   return CsvContainsInt(InpBlockedUtcHoursCsv, parts.hour) ||
          CsvContainsInt(InpBlockedPythonWeekdaysCsv, pythonWeekday);
}

bool HasManagedPosition()
{
   if(!PositionSelect(_Symbol))
      return false;
   return PositionGetInteger(POSITION_MAGIC) == InpMagicNumber;
}

ENUM_POSITION_TYPE ManagedPositionType()
{
   return (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);
}

void ResetTradeState()
{
   g_entryPrice = 0.0;
   g_initialRisk = 0.0;
   g_maxFavorableExcursion = 0.0;
   g_maxAdverseExcursion = 0.0;
   g_entryBarTime = 0;
   g_entryBarsSeen = 0;
   g_stopStage = 0;
}

void SyncStateFromPositionIfNeeded()
{
   if(!HasManagedPosition())
   {
      ResetTradeState();
      return;
   }
   if(g_entryPrice > 0.0 && g_initialRisk > 0.0)
      return;
   g_entryPrice = PositionGetDouble(POSITION_PRICE_OPEN);
   const double stopLoss = PositionGetDouble(POSITION_SL);
   g_initialRisk = MathAbs(g_entryPrice - stopLoss);
   g_entryBarTime = (datetime)PositionGetInteger(POSITION_TIME);
}

void UpdateExcursion(const MqlRates &bar)
{
   if(!HasManagedPosition())
      return;
   SyncStateFromPositionIfNeeded();
   if(g_initialRisk <= 0.0)
      return;
   const ENUM_POSITION_TYPE type = ManagedPositionType();
   if(type == POSITION_TYPE_BUY)
   {
      g_maxFavorableExcursion = MathMax(g_maxFavorableExcursion, bar.high - g_entryPrice);
      g_maxAdverseExcursion = MathMin(g_maxAdverseExcursion, bar.low - g_entryPrice);
   }
   else
   {
      g_maxFavorableExcursion = MathMax(g_maxFavorableExcursion, g_entryPrice - bar.low);
      g_maxAdverseExcursion = MathMin(g_maxAdverseExcursion, g_entryPrice - bar.high);
   }
}

void ManageBreakeven()
{
   if(!InpBreakevenStopEnabled || !HasManagedPosition())
      return;
   SyncStateFromPositionIfNeeded();
   if(g_initialRisk <= 0.0)
      return;
   const double mfeR = g_maxFavorableExcursion / g_initialRisk;
   if(mfeR < InpBreakevenTriggerMfeR)
      return;

   const ENUM_POSITION_TYPE type = ManagedPositionType();
   const double currentSl = PositionGetDouble(POSITION_SL);
   const double currentTp = PositionGetDouble(POSITION_TP);
   double newSl = currentSl;
   if(type == POSITION_TYPE_BUY)
      newSl = NormalizePrice(g_entryPrice + (g_initialRisk * InpBreakevenLockR));
   else
      newSl = NormalizePrice(g_entryPrice - (g_initialRisk * InpBreakevenLockR));

   const bool improves = (type == POSITION_TYPE_BUY && newSl > currentSl) ||
                         (type == POSITION_TYPE_SELL && (currentSl == 0.0 || newSl < currentSl));
   if(improves && ModifyManagedPositionStops(newSl, currentTp, "BREAKEVEN"))
   {
      g_stopStage = MathMax(g_stopStage, 1);
      DebugLog(StringFormat("BREAKEVEN_STOP | sl=%.5f | mfeR=%.3f", newSl, mfeR));
   }
}

bool CloseManagedPosition(const string reason)
{
   if(!HasManagedPosition())
      return false;
   if(!IsTradeSessionOpenNow())
      return false;
   trade.SetExpertMagicNumber(InpMagicNumber);
   trade.SetDeviationInPoints(InpSlippagePoints);
   const bool ok = trade.PositionClose(_Symbol);
   DebugLog(StringFormat("CLOSE_%s | ok=%s | retcode=%d", reason, ok ? "true" : "false", trade.ResultRetcode()));
   if(ok)
      ResetTradeState();
   return ok;
}

bool ManageTimeExits(const MqlRates &bar)
{
   if(!HasManagedPosition())
      return false;
   SyncStateFromPositionIfNeeded();
   if(g_initialRisk <= 0.0)
      return false;

   const double mfeR = g_maxFavorableExcursion / g_initialRisk;
   const int barsHeld = g_entryBarsSeen;

   if(InpHybridTimeDecayTriageEnabled && barsHeld == InpHybridTimeDecayCheckpoint)
   {
      const ENUM_POSITION_TYPE type = ManagedPositionType();
      const double unrealized = (type == POSITION_TYPE_BUY) ? (bar.close - g_entryPrice) : (g_entryPrice - bar.close);
      const double unrealizedR = unrealized / g_initialRisk;
      if(unrealizedR <= InpHybridTimeDecayMaxUnrealizedR && mfeR <= InpHybridTimeDecayMaxMfeR)
         return CloseManagedPosition("HYBRID_TIME_DECAY_TRIAGE");
   }

   if(InpTimeDecayExitEnabled && InpTimeDecayBars > 0 && barsHeld >= InpTimeDecayBars && mfeR < InpTimeDecayMinMfeR)
      return CloseManagedPosition("TIME_DECAY");

   return false;
}

double RiskLots(const double entryPrice, const double stopPrice)
{
   const double equity = AccountInfoDouble(ACCOUNT_EQUITY);
   const double riskMoney = equity * MathMax(0.0, InpRiskPct);
   const double stopDistance = MathAbs(entryPrice - stopPrice);
   const double tickSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   const double tickValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   const double contractSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_CONTRACT_SIZE);
   const double minLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   const double maxLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   const double step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);

   if(stopDistance <= 0.0 || tickSize <= 0.0 || tickValue <= 0.0 || step <= 0.0 || entryPrice <= 0.0)
      return 0.0;

   const double lossPerLot = (stopDistance / tickSize) * tickValue;
   double lots = riskMoney / lossPerLot;
   if(InpMaxLeverage > 0.0 && contractSize > 0.0)
   {
      const double maxNotional = equity * InpMaxLeverage;
      const double leverageLots = maxNotional / (entryPrice * contractSize);
      lots = MathMin(lots, leverageLots);
   }

   lots = MathFloor(lots / step) * step;
   lots = MathMax(minLot, MathMin(maxLot, lots));
   return NormalizeDouble(lots, 2);
}

bool OpenPosition(const int direction, const double atrValue)
{
   if(!IsTradeSessionOpenNow())
      return false;

   trade.SetExpertMagicNumber(InpMagicNumber);
   trade.SetDeviationInPoints(InpSlippagePoints);

   const double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   const double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   const double entry = direction == 1 ? ask : bid;
   const double stop = direction == 1
      ? NormalizePrice(entry - (atrValue * InpStopMult))
      : NormalizePrice(entry + (atrValue * InpStopMult));
   const double lots = RiskLots(entry, stop);
   if(lots <= 0.0)
      return false;

   bool ok = false;
   if(direction == 1)
      ok = trade.Buy(lots, _Symbol, 0.0, stop, 0.0, "StrategyLab MA long");
   else
      ok = trade.Sell(lots, _Symbol, 0.0, stop, 0.0, "StrategyLab MA short");

   DebugLog(StringFormat("OPEN_%s | ok=%s | lots=%.2f | entry=%.5f | sl=%.5f | atr=%.5f | retcode=%d",
                         direction == 1 ? "LONG" : "SHORT",
                         ok ? "true" : "false",
                         lots,
                         entry,
                         stop,
                         atrValue,
                         trade.ResultRetcode()));
   if(ok)
   {
      g_entryPrice = entry;
      g_initialRisk = MathAbs(entry - stop);
      g_maxFavorableExcursion = 0.0;
      g_maxAdverseExcursion = 0.0;
      g_entryBarTime = iTime(_Symbol, PERIOD_CURRENT, 0);
      g_entryBarsSeen = 0;
      g_stopStage = 0;
   }
   return ok;
}

int PriceFastCrossCount(const MqlRates &rates[], const int total)
{
   int count = 0;
   for(int shift = 1; shift <= InpNoiseLookback; ++shift)
   {
      if(shift + 1 >= total)
         break;
      const double fastNow = SimpleSmaClose(rates, shift, InpFastLen, total);
      const double fastPrev = SimpleSmaClose(rates, shift + 1, InpFastLen, total);
      if(fastNow == EMPTY_VALUE || fastPrev == EMPTY_VALUE)
         continue;
      const double previousRelation = rates[shift + 1].close - fastPrev;
      const double currentRelation = rates[shift].close - fastNow;
      if((previousRelation <= 0.0 && currentRelation > 0.0) ||
         (previousRelation >= 0.0 && currentRelation < 0.0))
         ++count;
   }
   return count;
}

void ProcessClosedBar()
{
   const int requiredBars = MathMax(MathMax(InpShortQualityGateLenBars + 5, InpSlowLen + 5),
                                    MathMax(InpAtrLen + 5, InpNoiseLookback + InpFastLen + 5));
   MqlRates rates[];
   if(!CopyRatesSafe(requiredBars, rates))
      return;
   const int total = ArraySize(rates);
   if(total < requiredBars)
      return;

   const int currentShift = 1;
   const int previousShift = 2;
   const MqlRates closedBar = rates[currentShift];

   if(HasManagedPosition())
   {
      ++g_entryBarsSeen;
      UpdateExcursion(closedBar);
      ManageBreakeven();
      if(ManageTimeExits(closedBar))
         return;
   }

   const double fastNow = SimpleSmaClose(rates, currentShift, InpFastLen, total);
   const double slowNow = SimpleSmaClose(rates, currentShift, InpSlowLen, total);
   const double fastPrev = SimpleSmaClose(rates, previousShift, InpFastLen, total);
   const double slowPrev = SimpleSmaClose(rates, previousShift, InpSlowLen, total);
   const double atrNow = SimpleAtr(rates, currentShift, InpAtrLen, total);
   if(fastNow == EMPTY_VALUE || slowNow == EMPTY_VALUE || fastPrev == EMPTY_VALUE || slowPrev == EMPTY_VALUE || atrNow == EMPTY_VALUE)
      return;

   const int crossCount = PriceFastCrossCount(rates, total);
   const bool crossCountOk = crossCount <= InpMaxNoCross;
   bool longSignal = InpAllowLong && crossCountOk && fastPrev <= slowPrev && fastNow > slowNow;
   bool shortSignal = InpAllowShort && crossCountOk && fastPrev >= slowPrev && fastNow < slowNow;

   if(shortSignal && InpShortQualityGateEnabled)
   {
      const double gateSma = SimpleSmaClose(rates, currentShift, InpShortQualityGateLenBars, total);
      if(gateSma == EMPTY_VALUE || closedBar.close < gateSma)
         shortSignal = false;
   }

   if((longSignal || shortSignal) && IsTimeRiskBlocked(closedBar.time))
   {
      DebugLog(StringFormat("TIME_RISK_BLOCK | time=%s", TimeToString(closedBar.time)));
      longSignal = false;
      shortSignal = false;
   }

   bool reverseBlocked = false;
   if(HasManagedPosition() && InpHybridReverseExitTriageEnabled)
   {
      SyncStateFromPositionIfNeeded();
      const ENUM_POSITION_TYPE type = ManagedPositionType();
      const double mfeR = g_initialRisk > 0.0 ? g_maxFavorableExcursion / g_initialRisk : 0.0;
      if(((type == POSITION_TYPE_BUY && shortSignal) || (type == POSITION_TYPE_SELL && longSignal)) &&
         mfeR < InpHybridReverseExitMinMfeR)
      {
         reverseBlocked = true;
         longSignal = false;
         shortSignal = false;
         DebugLog(StringFormat("REVERSE_BLOCK | mfeR=%.3f", mfeR));
      }
   }

   if(HasManagedPosition() && !reverseBlocked)
   {
      const ENUM_POSITION_TYPE type = ManagedPositionType();
      if(type == POSITION_TYPE_BUY && shortSignal)
         CloseManagedPosition("REVERSE");
      else if(type == POSITION_TYPE_SELL && longSignal)
         CloseManagedPosition("REVERSE");
   }

   if(!HasManagedPosition())
   {
      if(longSignal)
         OpenPosition(1, atrNow);
      else if(shortSignal)
         OpenPosition(-1, atrNow);
   }
}

int OnInit()
{
   trade.SetExpertMagicNumber(InpMagicNumber);
   trade.SetDeviationInPoints(InpSlippagePoints);
   ResetTradeState();
   DebugLog("StrategyLab MA Cross ATR Stop initialized.");
   return INIT_SUCCEEDED;
}

void OnTick()
{
   if(!NewBarFormed())
      return;
   ProcessClosedBar();
}
