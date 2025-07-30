# Copyright (c) 2005-2024 Real-Time Innovations, Inc.  All rights reserved.
# No duplications, whole or partial, manual or electronic, may be made
# without express written permission.  Any such copies, or revisions thereof,
# must display this notice unaltered.
# This code contains trade secrets of Real-Time Innovations, Inc.

import typing

uint8 = typing.NewType("uint8", int)
int8 = typing.NewType("int8", int)
char = typing.NewType("char", int)

int16 = typing.NewType("int16", int)
uint16 = typing.NewType("uint16", int)
wchar = typing.NewType("wchar", int)

int32 = typing.NewType("int32", int)
uint32 = typing.NewType("uint32", int)

int64 = int
uint64 = typing.NewType("uint64", int)

float32 = typing.NewType("float32", float)
float64 = float
