BTW EXTRA CREDIT: if-else nesting (O RLY? inside YA RLY and inside NO WAI, up to 3 levels deep)
HAI
  WAZZUP
    I HAS A a ITZ 0
    I HAS A b ITZ 0
    I HAS A c ITZ 0
  BUHBYE

  a R 10
  b R 5
  c R 1
  BTW is a > 5?
  DIFFRINT BIGGR OF a AN 5 AN 5
  O RLY?
    YA RLY
      BTW is b > 3?
      DIFFRINT BIGGR OF b AN 3 AN 3
      O RLY?
        YA RLY
          BOTH SAEM c AN 1
          O RLY?
            YA RLY
              VISIBLE "branch X1"
            NO WAI
              VISIBLE "branch X2"
          OIC
        NO WAI
          VISIBLE "branch Y"
      OIC
    NO WAI
      BOTH SAEM a AN 0
      O RLY?
        YA RLY
          VISIBLE "branch Z1"
        NO WAI
          VISIBLE "branch Z2"
      OIC
  OIC

  a R 10
  b R 5
  c R 2
  DIFFRINT BIGGR OF a AN 5 AN 5
  O RLY?
    YA RLY
      DIFFRINT BIGGR OF b AN 3 AN 3
      O RLY?
        YA RLY
          BOTH SAEM c AN 1
          O RLY?
            YA RLY
              VISIBLE "branch X1"
            NO WAI
              VISIBLE "branch X2"
          OIC
        NO WAI
          VISIBLE "branch Y"
      OIC
    NO WAI
      BOTH SAEM a AN 0
      O RLY?
        YA RLY
          VISIBLE "branch Z1"
        NO WAI
          VISIBLE "branch Z2"
      OIC
  OIC

  a R 10
  b R 1
  c R 1
  DIFFRINT BIGGR OF a AN 5 AN 5
  O RLY?
    YA RLY
      DIFFRINT BIGGR OF b AN 3 AN 3
      O RLY?
        YA RLY
          BOTH SAEM c AN 1
          O RLY?
            YA RLY
              VISIBLE "branch X1"
            NO WAI
              VISIBLE "branch X2"
          OIC
        NO WAI
          VISIBLE "branch Y"
      OIC
    NO WAI
      BOTH SAEM a AN 0
      O RLY?
        YA RLY
          VISIBLE "branch Z1"
        NO WAI
          VISIBLE "branch Z2"
      OIC
  OIC

  a R 0
  b R 5
  c R 1
  DIFFRINT BIGGR OF a AN 5 AN 5
  O RLY?
    YA RLY
      DIFFRINT BIGGR OF b AN 3 AN 3
      O RLY?
        YA RLY
          BOTH SAEM c AN 1
          O RLY?
            YA RLY
              VISIBLE "branch X1"
            NO WAI
              VISIBLE "branch X2"
          OIC
        NO WAI
          VISIBLE "branch Y"
      OIC
    NO WAI
      BOTH SAEM a AN 0
      O RLY?
        YA RLY
          VISIBLE "branch Z1"
        NO WAI
          VISIBLE "branch Z2"
      OIC
  OIC

  a R 3
  b R 5
  c R 1
  DIFFRINT BIGGR OF a AN 5 AN 5
  O RLY?
    YA RLY
      DIFFRINT BIGGR OF b AN 3 AN 3
      O RLY?
        YA RLY
          BOTH SAEM c AN 1
          O RLY?
            YA RLY
              VISIBLE "branch X1"
            NO WAI
              VISIBLE "branch X2"
          OIC
        NO WAI
          VISIBLE "branch Y"
      OIC
    NO WAI
      BOTH SAEM a AN 0
      O RLY?
        YA RLY
          VISIBLE "branch Z1"
        NO WAI
          VISIBLE "branch Z2"
      OIC
  OIC
KTHXBYE

BTW EXPECTED OUTPUT:
BTW branch X1  (a=10 b=5 c=1)
BTW branch X2  (a=10 b=5 c=2)
BTW branch Y   (a=10 b=1 c=1)
BTW branch Z1  (a=0  b=5 c=1)
BTW branch Z2  (a=3  b=5 c=1)
