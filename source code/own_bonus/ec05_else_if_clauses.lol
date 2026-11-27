BTW EXTRA CREDIT: else-if clauses (several MEBBEs: first true one wins; NO WAI optional)
HAI
  WAZZUP
    I HAS A temp ITZ 0
  BUHBYE

  temp R 100
  BOTH SAEM temp AN 100
  O RLY?
    YA RLY
      VISIBLE "boiling"
    MEBBE BOTH SAEM temp AN 37
      VISIBLE "body temperature"
    MEBBE DIFFRINT SMALLR OF temp AN 0 AN 0
      VISIBLE "below freezing"
    MEBBE DIFFRINT BIGGR OF temp AN 50 AN 50
      VISIBLE "very hot"
    NO WAI
      VISIBLE "normal"
  OIC

  temp R 37
  BOTH SAEM temp AN 100
  O RLY?
    YA RLY
      VISIBLE "boiling"
    MEBBE BOTH SAEM temp AN 37
      VISIBLE "body temperature"
    MEBBE DIFFRINT SMALLR OF temp AN 0 AN 0
      VISIBLE "below freezing"
    MEBBE DIFFRINT BIGGR OF temp AN 50 AN 50
      VISIBLE "very hot"
    NO WAI
      VISIBLE "normal"
  OIC

  temp R -5
  BOTH SAEM temp AN 100
  O RLY?
    YA RLY
      VISIBLE "boiling"
    MEBBE BOTH SAEM temp AN 37
      VISIBLE "body temperature"
    MEBBE DIFFRINT SMALLR OF temp AN 0 AN 0
      VISIBLE "below freezing"
    MEBBE DIFFRINT BIGGR OF temp AN 50 AN 50
      VISIBLE "very hot"
    NO WAI
      VISIBLE "normal"
  OIC

  temp R 75
  BOTH SAEM temp AN 100
  O RLY?
    YA RLY
      VISIBLE "boiling"
    MEBBE BOTH SAEM temp AN 37
      VISIBLE "body temperature"
    MEBBE DIFFRINT SMALLR OF temp AN 0 AN 0
      VISIBLE "below freezing"
    MEBBE DIFFRINT BIGGR OF temp AN 50 AN 50
      VISIBLE "very hot"
    NO WAI
      VISIBLE "normal"
  OIC

  BTW chain with no NO WAI and nothing matching: prints nothing
  temp R 25
  VISIBLE "before"
  BOTH SAEM temp AN 100
  O RLY?
    YA RLY
      VISIBLE "boiling"
    MEBBE BOTH SAEM temp AN 37
      VISIBLE "body temperature"
  OIC
  VISIBLE "after"
KTHXBYE

BTW EXPECTED OUTPUT:
BTW boiling
BTW body temperature
BTW below freezing
BTW very hot  (temp=75: both >50 is true, only the first matching MEBBE runs)
BTW before
BTW after
