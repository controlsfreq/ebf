Add two 32bit numbers
[-]>[-]>[-]>
>>>> move to b0
[
  -           decrement counter
  <<<<        move to a0
  +           increment a0
  <<<         move to c0
  +           increment c0
  >>>         move to a0
  [           decrement c0 if a0 is non-zero ~ no overflow
    <<<       move to c0
    -         decrement c0
    >>>       move to a0
  ]
  >>>>        move to b0
]
<<<< <<<      move to c0
[
  >>> >       move to a1
  +           increment a1
  < << + >> > increment c1
  [< << - >> >] decrement c1 if a1 is non-zero ~ no overflow
  < <<<
]
>>> >>>> > move to b1
[
  -           decrement counter
  <<<<        move to a1
  +           increment a1
  <<<         move to c1
  +           increment c1
  >>>         move to a1
  [           decrement c1 if a1 is non-zero ~ no overflow
    <<<       move to c1
    -         decrement c1
    >>>       move to a1
  ]
  >>>>        move to b1
]
<<<< <<<      move to c1
[
  >>> >       move to a2
  +           increment a2
  < << + >> > increment c2
  [< << - >> >] decrement c2 if a2 is non-zero ~ no overflow
  < <<<
]
>>> >>>> >> move to b2
[
  -           decrement counter
  <<<<        move to a2
  +           increment a2
  <<<         move to c2
  +           increment c2
  >>>         move to a2
  [           decrement c2 if a2 is non-zero ~ no overflow
    <<<       move to c2
    -         decrement c2
    >>>       move to a2
  ]
  >>>>        move to b2
]
<<<< <<<      move to c2
[
  >>> >       move to a3
  +           increment a3
  < << + >> > increment c3
  [< << - >> >] decrement c3 if a3 is non-zero ~ no overflow
  < <<<
]
>>> >>>> > move to b3