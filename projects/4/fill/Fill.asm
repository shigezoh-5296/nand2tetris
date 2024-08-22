// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, 
// the screen should be cleared.

(LOOP)
    @KBD
    D=M
    @i
    M=0
    @BLACK
    D;JNE
    @WHITE
    0;JMP

    (BLACK)
        @i
        D=M
        @SCREEN
        A=A+D
        M=0
        M=!M

        @i
        MD=M+1
        @8192
        D=A-D
        @BLACK
        D;JNE
        @LOOP
        0;JMP

    (WHITE)
        @i
        D=M
        @SCREEN
        A=A+D
        M=0

        @i
        MD=M+1
        @8192
        D=A-D
        @WHITE
        D;JNE
        @LOOP
        0;JMP