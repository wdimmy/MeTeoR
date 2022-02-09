CASES ={ "case_1":
  [
        ["P(a)@0", "R(a,b)@0", "R(b,c)@0", "R(c,a)@0"],
        ["R(X,Y):- Diamondminus[1,1]R(X,Y)", "Q(Y):- P(X), R(X,Y)", "P(X):- Diamondminus[1,1]Q(X)"],
        [2]
  ],
  "case_2":
   [
      ["P(a)@0", "R(a,b)@0", "R(b,c)@0", "R(c,d)@0", "R(d,e)@0", "R(e,f)@0", "R(f,g)@0", "R(g,h)@0"],
      ["R(X,Y):- Diamondminus[1,1]R(X,Y)", "Q(Y):- P(X), R(X,Y)", "P(X):- Diamondminus[1,1]Q(X)"],
      [2]
   ],
   "case_3":
    [
       ["A(a)@0"],
       ["B(X):- Diamondminus[1,2]A(X)", "B(X):- Diamondminus[2,3]A(X)", "A(X):- Boxminus[0,2]B(X)"],
       [6]
    ],
    "case_4":
    [
       ["A(a)@[0,2]"],
       ["B(X):- Boxminus[0,2]A(X)", "Boxplus[1,3]A(X):- B(X)", "C(X):- Boxplus[0,1]A(X)", "C(X):-Boxplus[1,2]A(X)"],
       [6]
    ],
    "case_5":
    [
       ["A(a)@[0,7]"],
       ["A(X):-Boxminus[3,7]A(X)"],
       [14]
    ],
    "case_6":
    [
        ["A(a)@[0,3]", "B(a)@[2,4]"],
        ["C(X):-A(X), B(X)", "A(X):-Diamondminus[3,5]C(X)", "B(X):-Diamondminus[5,6]C(X)"],
        [12]
    ],
    "case_7":
    [
        ["A(a)@[2,5]"],
        ["B(X):-A(X)", "B(X):-Boxminus[1,2]A(X)", "A(X):-Boxminus[10,12]B(X)"],
        [24]
    ],
    "case_8":
    [
        ["A(a)@[0,1]"],
        ["A(X):-Diamondminus[3,4]A(X)"],
        [8]
    ]
}


if __name__ == "__main__":
      pass