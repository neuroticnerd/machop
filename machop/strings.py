# -*- encoding: utf-8 -*-
from colorama import Fore as fore
from colorama import Style as style

ascii_choose_you = fore.RED + style.BRIGHT + "\n\
  ___        _                                              _ \n\
 |_ _|   ___| |__   ___   ___  ___  ___   _   _  ___  _   _| |\n\
  | |   / __| '_ \ / _ \ / _ \/ __|/ _ \ | | | |/ _ \| | | | |\n\
  | |  | (__| | | | (_) | (_) \__ \  __/ | |_| | (_) | |_| |_|\n\
 |___|  \___|_| |_|\___/ \___/|___/\___|  \__, |\___/ \__,_(_)\n\
                                          |___/               \n\
" + style.RESET_ALL

ascii_runaway = fore.RED + style.BRIGHT + "\n\
                         _                      \n\
    _ __ ___   __ _  ___| |__   ___  _ __       \n\
   | '_ ` _ \ / _` |/ __| '_ \ / _ \| '_ \      \n\
   | | | | | | (_| | (__| | | | (_) | |_) |     \n\
   |_| |_| |_|\__,_|\___|_| |_|\___/| .__/    _ \n\
  _ __ __ _ _ __     __ ___      ___|_| _   _| |\n\
 | '__/ _` | '_ \   / _` \ \ /\ / / _` | | | | |\n\
 | | | (_| | | | | | (_| |\ V  V / (_| | |_| |_|\n\
 |_|  \__,_|_| |_|  \__,_| \_/\_/ \__,_|\__, (_)\n\
                                        |___/   \n\
" + style.RESET_ALL

ascii_fainted = fore.RED + style.BRIGHT + "\n\
                       _                    __      _       _           _ _ \n\
  _ __ ___   __ _  ___| |__   ___  _ __    / _| ___(_)_ __ | |_ ___  __| | |\n\
 | '_ ` _ \ / _` |/ __| '_ \ / _ \| '_ \  | |_ / _ | | '_ \| __/ _ \/ _` | |\n\
 | | | | | | (_| | (__| | | | (_) | |_) | |  _| (_|| | | | | ||  __/ (_| |_|\n\
 |_| |_| |_|\__,_|\___|_| |_|\___/| .__/  |_|  \__,|_|_| |_|\__\___|\__,_(_)\n\
                                  |_|                                       \n\
" + style.RESET_ALL

ascii_machop = fore.CYAN + style.BRIGHT + "\
                          ,.=--.\n\
                      ,.-/    ,/\"\"-.\n\
                    ,/ ,'   ,\"      \\\n\
                   /' /   .''      __|\n\
                  .' ||  /,    _.\"   '.\n\
                  || ||  ||  ,'        `.\n\
                 /|| ||  ||,'            .\n\
                /.`/ /` /`,'  __          '\n\
               j /. \" `\"  ' ,' /`.        |\n\
               ||.|        .  | . .      _|,--._\n\
               ||#|        |  | #'|   ,-\"       `-.\n\
              /'.||        |  \.\" |  /             `\n\
             /    '        `.----\"   |`.|           |\n\
             \  `.    ,'             `  \           |\n\
              `._____           _,-'  `._,..        |\n\
                `\".  `'-..__..-'   _,.--'.  .       |\n\
                 ,-^-._      _,..-'       `.|       '\n\
             _,-'     |'\"\"'\"\"              `|  `\    \\\n\
         _.-'         |            `.,--    |    \    \\\n\
    _,.\"\"'\"\"'-._      '      `.     .      j      '    \\\n\
   /            `.___/.-\"    ._`-._  \.    |      |     L\n\
   L ____           /,.-'    . `._ '\"\"|`.  `      |     |\n\
   `.    `\"-.      / _,-\"     `._ `\"'\".  `. \     '     '\n\
     \       `-   .\"'            \"`---'\   ` `-._/     /\n\
      `-------.   |                     \   `-._      /\n\
               \ j                      .       `...,'\n\
                `|                       \\\n\
                 '                        \\\n\
                  .                      / \\\n\
                  |`.                   /   `._\n\
                  |    `.._____        /|      `-._\n\
                  |        |   Y.       |.         `.\n\
                  |       j     \       '.`\"--....-'\n\
               _,-'       |      |        \\\n\
            .-'           |     ,'         `.\n\
           '              |     |            `.\n\
           `.        __,.-'     '.             \\\n\
             `-.---\"'             `-..__      _/\n\
                                        `'\"\"\"'" + style.RESET_ALL

txt_startup_msg = "\n      *** use CTRL+C to terminate running commands ***\n"

txt_config_error = fore.RED + style.BRIGHT + "fatal exception:"
txt_config_error += style.RESET_ALL + " karatechop.py could not be loaded!\n\n"
txt_config_error += fore.YELLOW + style.BRIGHT + " *** hint" + style.RESET_ALL
txt_config_error += ": have you run 'machop init' in the current directory?\n"
txt_config_error += fore.YELLOW + style.BRIGHT + " *** hint" + style.RESET_ALL
txt_config_error += ": is your machop file in the current directory?\n"
txt_config_error += fore.YELLOW + style.BRIGHT + " *** hint" + style.RESET_ALL
txt_config_error += ": is your machop file named 'karatechop.py'?"

txt_machop = fore.CYAN + style.BRIGHT + "machop" + style.RESET_ALL
