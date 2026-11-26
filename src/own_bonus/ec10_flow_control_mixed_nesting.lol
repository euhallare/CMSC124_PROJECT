BTW EXTRA CREDIT: nesting of different flow-control statements (if/loop/switch inside each other)
HAI
  WAZZUP
    I HAS A n ITZ 1
    I HAS A k ITZ 0
    I HAS A kind ITZ 3
  BUHBYE

  BTW 1) if-else inside a loop
  IM IN YR classify UPPIN YR n TIL BOTH SAEM n AN 5
    BOTH SAEM MOD OF n AN 2 AN 1
    O RLY?
      YA RLY
        VISIBLE n + " is odd"
      NO WAI
        VISIBLE n + " is even"
    OIC
  IM OUTTA YR classify

  BTW 2) loop inside an if
  BOTH SAEM kind AN 3
  O RLY?
    YA RLY
      k R 1
      IM IN YR counter UPPIN YR k TIL BOTH SAEM k AN 4
        VISIBLE "step " + k
      IM OUTTA YR counter
    NO WAI
      VISIBLE "skipped"
  OIC

  BTW 3) switch inside a loop (GTFO leaves only the switch, the loop keeps going)
  n R 1
  IM IN YR switcher UPPIN YR n TIL BOTH SAEM n AN 4
    n
    WTF?
      OMG 1
        VISIBLE "one"
        GTFO
      OMG 2
        VISIBLE "two"
        GTFO
      OMGWTF
        VISIBLE "other"
    OIC
  IM OUTTA YR switcher

  BTW 4) loop inside a switch (kloop: k=2 down, TIL stops before printing k=0)
  kind
  WTF?
    OMG 1
      VISIBLE "kind one"
      GTFO
    OMG 3
      k R 2
      IM IN YR kloop NERFIN YR k TIL BOTH SAEM k AN 0
        VISIBLE "k=" + k
      IM OUTTA YR kloop
      GTFO
  OIC

  BTW 5) GTFO inside an if inside a loop breaks the loop (prints k=0,1,2 then stops at k=3)
  k R 0
  IM IN YR breaker UPPIN YR k TIL BOTH SAEM k AN 10
    BOTH SAEM k AN 3
    O RLY?
      YA RLY
        GTFO
    OIC
    VISIBLE "k=" + k
  IM OUTTA YR breaker
  VISIBLE "done"
KTHXBYE

BTW EXPECTED OUTPUT:
BTW 1 is odd
BTW 2 is even
BTW 3 is odd
BTW 4 is even
BTW step 1
BTW step 2
BTW step 3
BTW one
BTW two
BTW other
BTW k=2
BTW k=1
BTW k=0
BTW k=1
BTW k=2
BTW done
