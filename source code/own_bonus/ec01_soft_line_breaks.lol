BTW EXTRA CREDIT: soft-line/command breaks (,) - a comma acts like a newline
HAI
  WAZZUP
    I HAS A x ITZ 10, I HAS A y ITZ 20
    I HAS A z, I HAS A msg ITZ "hello"
  BUHBYE

  BTW commas between VISIBLE statements
  VISIBLE x, VISIBLE y
  BTW comma after assignment then print
  z R SUM OF x AN y, VISIBLE z
  BTW commas inside a YARN are plain text, not soft breaks
  VISIBLE "a, b, c", VISIBLE "done"
  BTW comma in a BTW comment is ignored
  VISIBLE msg BTW this comma, right here, is ignored
KTHXBYE

BTW EXPECTED OUTPUT:
BTW 10
BTW 20
BTW 30
BTW a, b, c
BTW done
BTW hello
