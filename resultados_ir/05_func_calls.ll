; Llamadas a función simples

; ModuleID = "bminor_program"
target triple = "unknown-unknown-unknown"
target datalayout = ""

define i32 @"inc"(i32 %"x")
{
entry:
  %"x.1" = alloca i32
  store i32 %"x", i32* %"x.1"
  %"x.2" = load i32, i32* %"x.1"
  %"addtmp" = add i32 %"x.2", 1
  ret i32 %"addtmp"
}

define i32 @"main"()
{
entry:
  %"t" = alloca i32
  store i32 10, i32* %"t"
  %"t.1" = load i32, i32* %"t"
  %"inc.call" = call i32 @"inc"(i32 %"t.1")
  store i32 %"inc.call", i32* %"t"
  %"t.2" = load i32, i32* %"t"
  ret i32 %"t.2"
}

