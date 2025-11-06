; print: string/char/int/bool

; ModuleID = "bminor_program"
target triple = "unknown-unknown-unknown"
target datalayout = ""

define i32 @"main"()
{
entry:
  %".2" = getelementptr inbounds [11 x i8], [11 x i8]* @"strlit_0", i32 0, i32 0
  %".3" = getelementptr inbounds [4 x i8], [4 x i8]* @"fmt_str_1", i32 0, i32 0
  %".4" = call i32 (i8*, ...) @"printf"(i8* %".3", i8* %".2")
  %"c" = alloca i8
  store i8 90, i8* %"c"
  %"c.1" = load i8, i8* %"c"
  %".6" = getelementptr inbounds [4 x i8], [4 x i8]* @"fmt_char_2", i32 0, i32 0
  %".7" = zext i8 %"c.1" to i32
  %".8" = call i32 (i8*, ...) @"printf"(i8* %".6", i32 %".7")
  %"x" = alloca i32
  store i32 42, i32* %"x"
  %"x.1" = load i32, i32* %"x"
  %".10" = getelementptr inbounds [4 x i8], [4 x i8]* @"fmt_int_3", i32 0, i32 0
  %".11" = call i32 (i8*, ...) @"printf"(i8* %".10", i32 %"x.1")
  %"t" = alloca i1
  %"x.2" = load i32, i32* %"x"
  %"cmptmp" = icmp sgt i32 %"x.2", 0
  store i1 %"cmptmp", i1* %"t"
  %"t.1" = load i1, i1* %"t"
  %".13" = getelementptr inbounds [4 x i8], [4 x i8]* @"fmt_bool_4", i32 0, i32 0
  %".14" = zext i1 %"t.1" to i32
  %".15" = call i32 (i8*, ...) @"printf"(i8* %".13", i32 %".14")
  ret i32 0
}

declare i32 @"printf"(i8* %".1", ...)

@"strlit_0" = internal constant [11 x i8] [i8 66, i8 45, i8 77, i8 105, i8 110, i8 111, i8 114, i8 32, i8 79, i8 75, i8 0]
@"fmt_str_1" = internal constant [4 x i8] [i8 37, i8 115, i8 10, i8 0]
@"fmt_char_2" = internal constant [4 x i8] [i8 37, i8 99, i8 10, i8 0]
@"fmt_int_3" = internal constant [4 x i8] [i8 37, i8 100, i8 10, i8 0]
@"fmt_bool_4" = internal constant [4 x i8] [i8 37, i8 100, i8 10, i8 0]
