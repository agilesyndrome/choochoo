
from contextlib import contextmanager
from logging import getLogger
from tempfile import TemporaryDirectory

from ch2 import constants
from ch2.commands.args import bootstrap_dir, V, DEV, FORCE, bootstrap_db
from ch2.common.args import mm, m
from ch2.config.profile.default import default
from ch2.srtm.bilinear import bilinear_elevation_from_constant
from ch2.srtm.file import SRTM1_DIR_CNAME
from ch2.srtm.spline import spline_elevation_from_constant
from tests import LogTestCase, random_test_user

log = getLogger(__name__)
ARCSEC = 1/3600


class TestSortem(LogTestCase):

    @contextmanager
    def bilinear(self):
        user = random_test_user()
        bootstrap_db(user, m(V), '5', mm(DEV), configurator=default)
        args, data = bootstrap_db(user, m(V), '5', 'constants', 'set', SRTM1_DIR_CNAME, '/home/andrew/archive/srtm1',
                                   mm(FORCE))
        constants(args, data)
        with data.db.session_context() as s:
            yield bilinear_elevation_from_constant(s)

    @contextmanager
    def spline(self, smooth=0):
        user = random_test_user()
        bootstrap_db(user, m(V), '5', mm(DEV), configurator=default)
        args, data = bootstrap_db(user, m(V), '5', 'constants', 'set', SRTM1_DIR_CNAME, '/home/andrew/archive/srtm1',
                                   mm(FORCE))
        constants(args, data)
        with data.db.session_context() as s:
            yield spline_elevation_from_constant(s, smooth=smooth)

    def test_read(self):
        with self.bilinear() as oracle:
            elevation = oracle.elevation(-33.4489, -70.6693)
            self.assertAlmostEqual(elevation, 544.9599999999932, places=9)
        with self.spline() as oracle:
            elevation = oracle.elevation(-33.4489, -70.6693)
            self.assertAlmostEqual(elevation, 545.1531644129972, places=9)

    def assert_contours(self, oracle, lat, lon, n, map, scale=1, step=1.):
        image = ''
        for i in range(n):
            y = lat + ARCSEC * i * step
            line = '\n'
            for j in range(n*2):
                x = lon + ARCSEC * j * step
                d = int(oracle.elevation(y, x) / scale) % 10
                line += ' .:-=+*#%@'[d]
            image += line
            print(line[1:])
        self.assertEqual(image, map)

    def test_interp_9_cells(self):

        with self.bilinear() as oracle:
            self.assert_contours(oracle, -33.5, -70.5, 30,
'''
======+++++++++++*********########%%%%%%%%%@@@@@@@@@@       
=========++++++++++********########%%%%%%%%%%@@@@@@@@@      
===========+++++++++********#########%%%%%%%%%@@@@@@@@@     
--==========+++++++++********#########%%%%%%%%%@@@@@@@@@    
----==========++++++++********#########%%%%%%%%%@@@@@@@@@   
------=========++++++++********#########%%%%%%%%%%@@@@@@@@@ 
--------========++++++++*********########%%%%%%%%%%@@@@@@@@@
::-------========++++++++*********########%%%%%%%%%%@@@@@@@@
::::------========+++++++++********#########%%%%%%%%%@@@@@@@
:::::-------=======+++++++++********#########%%%%%%%%%@@@@@@
::::::-------========++++++++********#########%%%%%%%%%@@@@@
..:::::-------=======+++++++++********#########%%%%%%%%%%@@@
..::::::-------=======++++++++*********##########%%%%%%%%%%%
...::::::-------=======++++++++*********##########%%%%%%%%%%
.....:::::-------=======++++++++*********###########%%%%%%%%
......:::::------=======+++++++++**********############%%%%%
 .....::::::------=======+++++++++**********#############%%%
  .....::::::------=======+++++++++***********##############
   ......:::::-----========+++++++++************############
    ......:::::-----=======++++++++++*************##########
     .....:::::-----========++++++++++***************#######
     ......:::::-----========+++++++++++***************#####
     ......:::::------========++++++++++++***************###
     ......::::::-----=========+++++++++++++****************
      ......:::::------==========++++++++++++***************
      ......::::::------==========+++++++++++++*************
      .......:::::-------===========++++++++++++************
      .......::::::-------============++++++++++++**********
       ......::::::--------=============++++++++++++********
       .......::::::---------=============++++++++++++******''', scale=10, step=1/10)

        with self.spline() as oracle:
            self.assert_contours(oracle, -33.5, -70.5, 30,
'''
======++++++++++++********########%%%%%%%%%%@@@@@@@@@       
========+++++++++++********########%%%%%%%%%%@@@@@@@@@      
==========++++++++++********########%%%%%%%%%%@@@@@@@@@     
-===========++++++++++*******#########%%%%%%%%%@@@@@@@@@    
----=========++++++++++*******#########%%%%%%%%%@@@@@@@@@   
------=========+++++++++********########%%%%%%%%%@@@@@@@@@  
-------=========+++++++++********########%%%%%%%%%@@@@@@@@@ 
::-------========+++++++++********########%%%%%%%%%@@@@@@@@@
::::------=========++++++++********#########%%%%%%%%@@@@@@@@
:::::------=========++++++++********#########%%%%%%%%%@@@@@@
::::::-------=======+++++++++********#########%%%%%%%%%@@@@@
..:::::-------=======+++++++++********#########%%%%%%%%%%@@@
...::::::------=======+++++++++********##########%%%%%%%%%%@
....::::::------=======++++++++*********##########%%%%%%%%%%
......:::::-----=======+++++++++*********###########%%%%%%%%
 ......:::::-----=======+++++++++*********#############%%%%%
  ......:::::-----=======+++++++++**********#############%%%
   .....:::::-----=======++++++++++**********###############
    .....:::::-----=======++++++++++***********#############
     .....:::::----========++++++++++*************##########
     .....:::::-----=======+++++++++++***************#######
      .....:::::----========++++++++++++****************####
      .....:::::-----========+++++++++++++*****************#
      ......::::------=========+++++++++++++****************
       .....:::::-----==========+++++++++++++***************
       .....:::::------===========+++++++++++++*************
       ......:::::------============++++++++++++************
       ......:::::-------==============+++++++++++**********
       ......::::::-------===============++++++++++*********
       .......::::::--------==============+++++++++++*******''', scale=10, step=1/10)

        with self.bilinear() as bilinear:

            class Delta:

                def __init__(self, spline):
                    self._spline = spline

                def elevation(self, x, y):
                    b = bilinear.elevation(x, y)
                    s = self._spline.elevation(x, y)
                    delta = b - s
                    return delta

            with self.spline(0) as spline:

                self.assert_contours(Delta(spline), -33.5, -70.5, 30,
'''
                                                            
                                                            
                                                            
                                                            
                                                            
                                                            
                                                            
                                                            
                                                            
                                                            
                                                            
                                                            
.....                                                       
.......                                                     
::::.....                                                   
::::::....                                                  
::::::....                                                  
.::::::...                                                  
...::.....                                                  
 ........                                                   
                                                            
  .......              @@@@                                 
  ........            @@@@@@                                
 .........            @@@@@@@                               
  ........            @@@@@@@                               
  ........            @@@@@@@                               
    .....             @@@@@@@                               
                      @@@@@@@                               
                      @@@@@@                                
                       @@@@@                                ''', scale=1, step=1/10)

            with self.spline(1) as spline:

                self.assert_contours(Delta(spline), -33.5, -70.5, 30,
'''
@%%##**++=----::::.......                 @@@@@@%%%%@@@@@@  
%###**++==----::::..........              @@@@@@@@%@@@@@@   
##***+++==----::::...........             @@@@@@@@@@@@@@@   
*+++++====----:::::..........              @@@@@@@@@@@@@    
=========-----:::::..........               @@@@@@@@@@@     
--------------::::::.........                @@@@@@@@@      
:::-----------::::::.........                 @@@@@@@       
...::::::----::::::::........                               
   ...:::::::::::::::.......                                
@     ..::::::::::::::......                                
%%@    ..:::::::::::::......                                
#%@@    ..::::::::::::::......                              
#%%@@    ...::::::::-:::::......                      @@@@  
##%%@@    ...:::::-----::::::.....                @@@@@@@@@@
*##%%@     ...::::-------::::::....            @@@@@@@@@@%%%
**##%@@     ...::---=------:::::....          @@@@@@@%%%%%%%
+**##%@@@    ..::---===------::::....         @@@@@@%%%%%###
=+**##%%@@   ..::--=====-------:::....       @@@@@@%%%%#####
=++**##%%@@   ..:--=======------:::...       @@@@%%%%####***
-=++**##%%@@  ..:--=++======----:::...       @@@%%%%###****+
--==+**##%%@   .:--=+++=======---:::...     @@@@%%%###***+++
-=++**##%%@@  ..:-==+++=======---::...      @@@@%%%%##****++
=++**##%%@@   .::-==+++======---:::..       @@@@%%%%###****+
++**##%%@@@   .::-==+++======---::...      @@@@@%%%%####****
+**##%%@@@   ..::-==++======----::..      @@@@@@%%%%%###****
*##%%%@@@    ..:--==++======----::..     @@@@@@%%%%%%####***
##%%%@@@     .::--==+======----::..     @@@@@@%%%%%%%%####**
#%%%@@      ..::--========-----::..    @@@@@%%%%%%@%%%#####*
%%@@@       ..::--=======------::.    @@@%%%%%%%%@@%%%%#####
%@@@       ...::---=====-------:..    @@%%%%%%%%%@@%%%%#####''', scale=1, step=1/10)

            with self.spline(10) as spline:

                self.assert_contours(Delta(spline), -33.5, -70.5, 30,
'''
.    @@%%####*******+*******##############***********####%%%
  @@%%%###********+++++******###############********####%%%%
%%%####***++++++++++++++******#########################%%%%%
******+++++++++++++++++++**********###################%%%%%@
===================++++++++**********################%%%%%@@
::--------============++++++*********##############%%%%%%@@@
 ....::::------========++++++********############%%%%%%%@@@@
@@@   ..::::------======++++++*******##########%%%%%%%@@@@@@
##%%@@  ..:::::-----=====++++++*******#######%%%%%%%%@@@@@@ 
++*##%%@  ...::::----======+++++******######%%%%%%%@@@@@@   
-==+*##%@  ....:::----======+++++*****#####%%%%%%@@@@@@@    
:--=+**#%@@  ...::---=====+++++******#####%%%%%%%%@@@@@@@@  
.:--=+**#%@@  ..::--=====+++++*****######%%%%%%%%%@@@@@@@@@@
 .::-=+**#%%@  ..:--====++++******######%%%%%%%%%%%%%%%@@@@@
@ .::-=+**#%%@  .::-===++++*****#######%%%%%%%%%%%%%%%%%%%%%
%@ ..:-=++*#%@@ .::-===+++****########%%%%%%%%%%%%%%%%%%%%%%
#%@ ..:-=++*#%@ .::-==++++***#######%%%%%%%%%%%%%%%%%%%%%###
*#%@  .:-=+*#%@@ .:-=++++***######%%%%%%%%%%%%%%%%%%%%######
+*#%@  .:-=+*#%@ .:-=+++***####%%%%%%%%%%%%%%%%%%%%%#######*
=+*#%@  .:-=+*%@ .:-++++***###%%%%%%%%%%%%%%%%%%%%%#####****
-=+*#%@  .:-+*#% .:-+++***###%%%%%%%%%%%@%%%%%%%%%%####****+
=+**#%@ .::=+*#% .:-+++***###%%%%%%%%%%%%%%%%%%%%%%%####****
=+*#%%@ .:-=+*#@ .:-=+++**###%%%%%%%%%%%%%%%%%%%%%%%%####***
+**#%@  .:-=+*#@ .:-=+++***###%%%%%%%%%%%%%%%%%%%%%%%%#####*
+*#%%@ .::-=+*%@ .:-=+++***###%%%%%%%%%%%%%%%%%%%%%%%%%#####
**#%@@ .:--=+#%@ .:-==++***###%%%%%%%%%%#%%%%%%%%@@%%%%%%###
*#%%@ ..:--+*#%@ .:-==+++**###%%%#########%%%%%%%@@@%%%%%%%#
*#%@@ .::-=+*#%@ .:-==+++***##%############%%%%%@@@@@@%%%%%%
#%%@  .::-=+*#%@ .:-===++***################%%%%@@@@@@@%%%%%
#%@@ ..:--=+*#%@ .::-==+++**############*###%%%%@@@@@@@@@%%%''', scale=1, step=1/10)

    def test_interp_4_tiles(self):

        with self.bilinear() as oracle:
            self.assert_contours(oracle, -34-10*ARCSEC, -71-20*ARCSEC, 20,
'''
:  @#*++=:. @@  ::-----==+*##@ .-=+#@@.=
:.@@#++=-:. @@ .:-=+==++**##%@ :-=+#%@ :
: @%#++=-:.    .:-=++***##%@ .::--+*%%@.
 @%##*+=-:.    .:-=+*##%%@  .:--=++*##@.
 @##*+=--::.....::-=*#%@  ..:-==+**#%%@.
@@#**+==--:......:-=+*%@ .::-=+**###%@ .
@%#*+++==--:.....:--+*#%@ ..:-++*#%%@ .-
%%##****+==::...::--=+*#%@@ .:-=+#%@ .-=
@%%%##%%#*+--:.:::--==+*#%%@ .:-=*#% :-+
  @@@@@@%#+=--::::--===+*##%@ ::=+*#@.-=
:::...  %#*+=-:::--===++++*#% ..:=+*%@.-
==--::. @%#++=----==++++++**#%@ :-=+#@.:
**+=-:. @%##*==---=********##%%@.-=+# .:
%##*+-:. @%%#+====+**#########%@.-=+#@.:
@%%#+=-:. @@#*====+**##%%%%%%%%@.-=+#@ :
. @#*+=-::. %#*+==+*##%@@@@@@%@@.-=*#@ :
: @%*++=-::.@%#*+++*##%@ ... @@ .-=+#%@.
=. %#*++=-:. %#**++*##% .:::.   .:=+*#% 
=:.@%#**+=-:.@##****#%@.:---::...:-=+*#@
+-. %##*+=:. @%#****#% .-=+==-:::::-=+*%''', scale=10, step=1)

        with self.spline() as oracle:
            self.assert_contours(oracle, -34-10*ARCSEC, -71-20*ARCSEC, 20,
'''
:  @#*++=:. @@  ::----===+*##@ .-=+#@@:=
:.@@*+==-:. @@ .:-=+==++**##%@ :-=+#%@ :
: @%#++=-:.    .:-=+****##%@ .::--+##%@.
 @%##*+=-:.    .:-=+*##%%@  .:--=++*##@.
 @##*+=--::.....::-=*#%@  ..:-==+**#%%@.
@@#**+==--:......:-=+*%@ .::-=+**###%@ .
@%#*+++==--:.....:-=+*#%@ ..:=++##%%@ .-
%##*****+==::...::--=+*#%@@ .:-=+#%@ .-=
@%%%%#%%#*+--:.:::--==+*#%%@ .:-=*#% :=+
  @@@@@@%#+=--::::--===+*##%@.::=+*#@.-=
:::...  %#*+=--::--===+++**#% ..:=+*%@.-
===-::. @%#++=----=+++++++**#%@ :-=+#@.:
**+=-:. @%##*==---=********##%%@.-=+# .:
%##*+-:. @%%#+====+**#########%@.-=+#@.:
@%%#+=-:. @@#*===++**##%%%%%%%%@.-=+#@ :
. @#*+=-::. %#*+==+*##%@@@@@@%@@.-=*#@ :
: @%*++=-::.@%#*+++*##%@ ... @@ .-=*#%@.
=. %#*++=-:. %#*+++*##% .:::.   .:=+*#% 
=:.@%#**+=-:.@%#**+*#%@.:---::...:-=+*#@
+-. %#**+=:. @%#***##% .-=+==-:::::-=+*%''', scale=10, step=1)

        with self.spline(1) as oracle:
            self.assert_contours(oracle, -34-10*ARCSEC, -71-20*ARCSEC, 20,
'''
:.@%##*+=-.  @  .:----===+*##@ .-=*#@ :=
: @%#*+=-:.    .:-====+++*##%@ .-=+*%@.:
. %#*+=-::.    .:-=++***#%%@ ..:-=+*#%@.
.@%#*+=-::.    .:-=+*##%%@ ..:--=++*#%@ 
 @%#*+=--:... ..:-=+*#%%@ .:--==+**##%@ 
@%#**++=--:.....::-=+*#%@ .:-==+**#%%@ .
%%#***++=--:.....:-==*#%@ .:--=+*#%@@ :-
%%##****+==-:....::-=+*#%@ .:-=+*#%@ .-=
@%%%%%##**+=-:..::---=+*#%%@ .:-+*#% :-+
  @@@@@%%#+=-:::::--===+**#%@ .:-+*%@.-=
:::... @%#*+=--::--===++++*#% .:-=+*%@.-
==--:.. @#*+==----=+++++++**#%@ :-=*#@.-
**+=-:. @%#*+==--==+********#%@ .:=*#@.:
%#*+=-:. @%#*++===++*########%%@.:=*#@.:
@@%*+=-:.. @#*++==+*###%@%%%%%@@.:=*#@.:
. @#*+=-::. %#*++=+*##%@@ @@@@@ .:=*#@ .
:.@%#*+=--: @%**+++*##%@ ..     .:=+#%@.
-: @#**+=-:. %#*+++*##@ .::...  .:-+*#% 
=:.@%#*+=-:. @#**++*#%@.:---::...:-=+*#@
=-.@%#*+=-:. @%#****#% .-====--::::-=+*#''', scale=10, step=1)

    def test_edges(self):
        for source in self.bilinear, self.spline:
            with source() as oracle:
                delta = 0.00000001
                lat, lon = -34, -71
                for dj in (-1, 0, 1):
                    y = lat + dj * delta
                    for di in (-1, 0, 1):
                        x = lon + di * delta
                        self.assertAlmostEqual(oracle.elevation(y, x), 645, places=2,
                                               msg='dj %d; di %d' % (dj, di))
