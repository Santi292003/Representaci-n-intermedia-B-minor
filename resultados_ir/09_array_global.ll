; Arreglo global 1D

; ModuleID = "bminor_program"
target triple = "unknown-unknown-unknown"
target datalayout = ""

define i32 @"main"()
{
entry:
  %".2" = getelementptr inbounds [4 x i32], [4 x i32]* @"a", i32 0, i32 0
  store i32 2, i32* %".2"
  %".4" = getelementptr inbounds [4 x i32], [4 x i32]* @"a", i32 0, i32 1
  store i32 4, i32* %".4"
  %".6" = getelementptr inbounds [4 x i32], [4 x i32]* @"a", i32 0, i32 2
  store i32 6, i32* %".6"
  %".8" = getelementptr inbounds [4 x i32], [4 x i32]* @"a", i32 0, i32 3
  store i32 8, i32* %".8"
  %"i" = alloca i32
  store i32 2, i32* %"i"
  %"x" = alloca i32
  %"i.1" = load i32, i32* %"i"
  %".11" = getelementptr inbounds [4 x i32], [4 x i32]* @"a", i32 0, i32 %"i.1"
  %"a.elem" = load i32, i32* %".11"
  store i32 %"a.elem", i32* %"x"
  %"y" = alloca i32
  %"i.2" = load i32, i32* %"i"
  %"subtmp" = sub i32 %"i.2", 1
  %".13" = getelementptr inbounds [4 x i32], [4 x i32]* @"a", i32 0, i32 %"subtmp"
  %"a.elem.1" = load i32, i32* %".13"
  store i32 %"a.elem.1", i32* %"y"
  %"x.1" = load i32, i32* %"x"
  %"y.1" = load i32, i32* %"y"
  %"addtmp" = add i32 %"x.1", %"y.1"
  ret i32 %"addtmp"
}

@"a" = global [4 x i32] zeroinitializer
