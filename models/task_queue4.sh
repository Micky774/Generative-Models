#!/bin/bash

dir=$(cd -P -- "$(dirname -- "$0")" && pwd -P)


python 3DConv.py --epochs 30 --lsdim 16 --pseudos 25 --batch-size 50 --lr 1e-1 --plr 1e-3 --log obs4/pl3_l1 --save weights/exp11/pl3_l1.h5;
python 3DConv.py --epochs 30 --lsdim 16 --pseudos 25 --batch-size 50 --lr 1e-2 --plr 1e-3 --log obs4/pl3_l2 --save weights/exp11/pl3_l2.h5;
python 3DConv.py --epochs 30 --lsdim 16 --pseudos 25 --batch-size 50 --lr 1e-3 --plr 1e-3 --log obs4/pl3_l3 --save weights/exp11/pl3_l3.h5;
python 3DConv.py --epochs 30 --lsdim 16 --pseudos 25 --batch-size 50 --lr 1e-4 --plr 1e-3 --log obs4/pl3_l4 --save weights/exp11/pl3_l4.h5;
python 3DConv.py --epochs 30 --lsdim 16 --pseudos 25 --batch-size 50 --lr 1e-1 --plr 1e-4 --log obs4/pl4_l1 --save weights/exp11/pl4_l1.h5;
python 3DConv.py --epochs 30 --lsdim 16 --pseudos 25 --batch-size 50 --lr 1e-2 --plr 1e-4 --log obs4/pl4_l2 --save weights/exp11/pl4_l2.h5;
python 3DConv.py --epochs 30 --lsdim 16 --pseudos 25 --batch-size 50 --lr 1e-3 --plr 1e-4 --log obs4/pl4_l3 --save weights/exp11/pl4_l3.h5;
python 3DConv.py --epochs 30 --lsdim 16 --pseudos 25 --batch-size 50 --lr 1e-4 --plr 1e-4 --log obs4/pl4_l4 --save weights/exp11/pl4_l4.h5;
python 3DConv.py --epochs 30 --lsdim 16 --pseudos 25 --batch-size 50 --lr 1e-1 --plr 1e-5 --log obs4/pl5_l1 --save weights/exp11/pl5_l1.h5;
python 3DConv.py --epochs 30 --lsdim 16 --pseudos 25 --batch-size 50 --lr 1e-2 --plr 1e-5 --log obs4/pl5_l2 --save weights/exp11/pl5_l2.h5;
python 3DConv.py --epochs 30 --lsdim 16 --pseudos 25 --batch-size 50 --lr 1e-3 --plr 1e-5 --log obs4/pl5_l3 --save weights/exp11/pl5_l3.h5;
python 3DConv.py --epochs 30 --lsdim 16 --pseudos 25 --batch-size 50 --lr 1e-4 --plr 1e-5 --log obs4/pl5_l4 --save weights/exp11/pl5_l4.h5;


