BTW EXTRA CREDIT: switch-nesting (WTF? inside an OMG block). No fall-through is relied on.
HAI
  WAZZUP
    I HAS A category ITZ 2
    I HAS A subcategory ITZ 1
  BUHBYE

  category
  WTF?
    OMG 1
      VISIBLE "category one"
      GTFO
    OMG 2
      VISIBLE "category two"
      subcategory
      WTF?
        OMG 1
          VISIBLE "sub one"
          GTFO
        OMG 2
          VISIBLE "sub two"
          GTFO
        OMGWTF
          VISIBLE "sub default"
      OIC
      VISIBLE "back in category two"
      GTFO
    OMGWTF
      VISIBLE "category default"
  OIC
  VISIBLE "done"

  BTW same shape, subcategory now hits the sub default
  subcategory R 9
  category
  WTF?
    OMG 1
      VISIBLE "category one"
      GTFO
    OMG 2
      VISIBLE "category two"
      subcategory
      WTF?
        OMG 1
          VISIBLE "sub one"
          GTFO
        OMG 2
          VISIBLE "sub two"
          GTFO
        OMGWTF
          VISIBLE "sub default"
      OIC
      VISIBLE "back in category two"
      GTFO
    OMGWTF
      VISIBLE "category default"
  OIC
  VISIBLE "done"

  BTW outer now hits the category default
  category R 7
  category
  WTF?
    OMG 1
      VISIBLE "category one"
      GTFO
    OMG 2
      VISIBLE "category two"
      GTFO
    OMGWTF
      VISIBLE "category default"
  OIC
  VISIBLE "done"
KTHXBYE

BTW EXPECTED OUTPUT:
BTW category two
BTW sub one
BTW back in category two
BTW done
BTW category two
BTW sub default
BTW back in category two
BTW done
BTW category default
BTW done
