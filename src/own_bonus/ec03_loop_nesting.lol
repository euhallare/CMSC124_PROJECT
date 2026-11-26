BTW EXTRA CREDIT: loop-nesting (loops inside loops, each with its own label)
HAI
  WAZZUP
    I HAS A r ITZ 1
    I HAS A c ITZ 1
    I HAS A sum ITZ 0
  BUHBYE

  BTW two levels: print addition table 1+1 to 3+3
  IM IN YR rowloop UPPIN YR r TIL BOTH SAEM r AN 4
    c R 1
    IM IN YR colloop UPPIN YR c TIL BOTH SAEM c AN 4
      VISIBLE r + "+" + c + "=" + SUM OF r AN c
    IM OUTTA YR colloop
  IM OUTTA YR rowloop

  BTW outer counts up (UPPIN/WILE), inner counts down (NERFIN/TIL)
  r R 1
  IM IN YR outer UPPIN YR r WILE DIFFRINT r AN 4
    c R r
    IM IN YR inner NERFIN YR c TIL BOTH SAEM c AN 0
      VISIBLE "r=" + r + " c=" + c
    IM OUTTA YR inner
  IM OUTTA YR outer
KTHXBYE

BTW EXPECTED OUTPUT:
BTW 1+1=2
BTW 1+2=3
BTW 1+3=4
BTW 2+1=3
BTW 2+2=4
BTW 2+3=5
BTW 3+1=4
BTW 3+2=5
BTW 3+3=6
BTW r=1 c=1
BTW r=2 c=2
BTW r=2 c=1
BTW r=3 c=3
BTW r=3 c=2
BTW r=3 c=1
