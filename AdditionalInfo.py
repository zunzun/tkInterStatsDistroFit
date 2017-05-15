links = '''
URL for source code of this computer program:
https://github.com/zunzun/tkInterStatsDistroFit

URL for web version of this code:
https://github.com/zunzun/zunzunsite3

URL for the pyeq3 fitting library, which has hundreds \
of known 2D and 3D equations:
https://github.com/zunzun/pyeq3
'''

author = '''
This is James Phillips, author of tkInterStatsDistroFit. My background \
is in nuclear engineering and industrial radiation physics, as I started \
working in the U.S. Navy as a submarine nuclear reactor operator \
many, many neutrons ago.

I have quite a bit of international experience calibrating industrial \
metal thickness and coating gauges. For example the thicker a piece of \
steel the more radiation it absorbs, and measuring the amount of radiation \
that passes through a sheet of steel can tell you how thick it is without \
touching it. Another example is that the thicker a zinc coating on steel \
sheets, the more zinc X-ray fluorescence energy it can emit - again allowing \
accurate thickness measurement for industrial manufacture.

My post-Navy employer originally used ad-hoc spreadsheets to very \
tediously create 4th-order polynomials calibrating to readings from \
known samples. So I started writing my own curve-fitting software in C.

When X-rays pass through aluminium, the atomic number of the alloying \
elements is much greater than that of the aluminium itself such that \
small changes in alloy composition lead to large changes in X-ray \
transmission for the same thickness. Alloy changes look like thickness \
changes, egad! However, alloy changes also cause changes to the X-rays \
that are scattered back from the aluminium, so that if both the transmitted \
and backscattered radiation is measured a more alloy-insensitive thickness \
measurement can be made - but this is now a 3D surface fit, and I started \
writing surface fitting software. I began to do considerable international work.

This finally led to the development of my Python fitting libraries, and \
this example tkinter statistical distributions fitter.

I hope you find this code useful, and to that end I have sprinkled \
explanatory comments throughout the code.  If you have any questions, \
comments or suggestions, please e-mail me directly at zunzun@zunzun.com \
or by posting to the user group at the URL
https://groups.google.com/forum/#!forum/zunzun_dot_com

I will be glad to help you.

James R. Phillips
2548 Vera Cruz Drive
Birmingham, AL 35235 USA

email: zunzun@zunzun.com
'''
