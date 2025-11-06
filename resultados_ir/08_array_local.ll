; Arreglo local 1D

; ModuleID = "bminor_program"
target triple = "unknown-unknown-unknown"
target datalayout = ""

define i32 @"main"()
{
entry:
  %"a" = alloca [5 x i32]
  %"i" = alloca i32
  store i32 0, i32* %"i"
  %"sum" = alloca i32
  store i32 0, i32* %"sum"
  %".4" = getelementptr inbounds [5 x i32], [5 x i32]* %"a", i32 0, i32 0
  store i32 5, i32* %".4"
  %".6" = getelementptr inbounds [5 x i32], [5 x i32]* %"a", i32 0, i32 1
  store i32 7, i32* %".6"
  %".8" = getelementptr inbounds [5 x i32], [5 x i32]* %"a", i32 0, i32 2
  store i32 9, i32* %".8"
  store i32 1, i32* %"i"
  %".11" = getelementptr inbounds [5 x i32], [5 x i32]* %"a", i32 0, i32 0
  %"a.elem" = load i32, i32* %".11"
  %"i.1" = load i32, i32* %"i"
  %".12" = getelementptr inbounds [5 x i32], [5 x i32]* %"a", i32 0, i32 %"i.1"
  %"a.elem.1" = load i32, i32* %".12"
  %"addtmp" = add i32 %"a.elem", %"a.elem.1"
  %"i.2" = load i32, i32* %"i"
  %"addtmp.1" = add i32 %"i.2", 1
  %".13" = getelementptr inbounds [5 x i32], [5 x i32]* %"a", i32 0, i32 %"addtmp.1"
  %"a.elem.2" = load i32, i32* %".13"
  %"addtmp.2" = add i32 %"addtmp", %"a.elem.2"
  store i32 %"addtmp.2", i32* %"sum"
  %"sum.1" = load i32, i32* %"sum"
  ret i32 %"sum.1"
}

