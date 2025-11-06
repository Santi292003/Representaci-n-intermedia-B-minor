; ++/-- pre y post mix

; ModuleID = "bminor_program"
target triple = "unknown-unknown-unknown"
target datalayout = ""

define i32 @"main"()
{
entry:
  %"i" = alloca i32
  store i32 2, i32* %"i"
  %"a" = alloca i32
  %"i.ld" = load i32, i32* %"i"
  %"i.inc" = add i32 %"i.ld", 1
  store i32 %"i.inc", i32* %"i"
  store i32 %"i.inc", i32* %"a"
  %"b" = alloca i32
  %"i.ld.1" = load i32, i32* %"i"
  %"i.inc.1" = add i32 %"i.ld.1", 1
  store i32 %"i.inc.1", i32* %"i"
  store i32 %"i.ld.1", i32* %"b"
  %"c" = alloca i32
  %"i.ld.2" = load i32, i32* %"i"
  %"i.dec" = sub i32 %"i.ld.2", 1
  store i32 %"i.dec", i32* %"i"
  store i32 %"i.dec", i32* %"c"
  %"d" = alloca i32
  %"i.ld.3" = load i32, i32* %"i"
  %"i.dec.1" = sub i32 %"i.ld.3", 1
  store i32 %"i.dec.1", i32* %"i"
  store i32 %"i.ld.3", i32* %"d"
  %"a.1" = load i32, i32* %"a"
  %"b.1" = load i32, i32* %"b"
  %"addtmp" = add i32 %"a.1", %"b.1"
  %"c.1" = load i32, i32* %"c"
  %"addtmp.1" = add i32 %"addtmp", %"c.1"
  %"d.1" = load i32, i32* %"d"
  %"addtmp.2" = add i32 %"addtmp.1", %"d.1"
  %"i.1" = load i32, i32* %"i"
  %"addtmp.3" = add i32 %"addtmp.2", %"i.1"
  ret i32 %"addtmp.3"
}

