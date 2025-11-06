; Float: operaciones y comparación

; ModuleID = "bminor_program"
target triple = "unknown-unknown-unknown"
target datalayout = ""

define i32 @"main"()
{
entry:
  %"a" = alloca double
  store double 0x4000000000000000, double* %"a"
  %"b" = alloca double
  store double 0x4008000000000000, double* %"b"
  %"r" = alloca i32
  store i32 0, i32* %"r"
  %"a.1" = load double, double* %"a"
  %"b.1" = load double, double* %"b"
  %"fmultmp" = fmul double %"a.1", %"b.1"
  %"fcmptmp" = fcmp ogt double %"fmultmp", 0x4014000000000000
  br i1 %"fcmptmp", label %"if.then", label %"if.end"
if.then:
  store i32 1, i32* %"r"
  br label %"if.end"
if.end:
  %"r.1" = load i32, i32* %"r"
  ret i32 %"r.1"
}

