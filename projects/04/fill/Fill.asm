// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.
    @v8k
    D=1
    D=D+1
    M=D
    M=M+D
    D=M
    M=M+D // M=8
    D=M
    M=M+D // M=16
    D=M
    M=M+D // M=32
    D=M
    M=M+D // M=64
    D=M
    M=M+D // M=128
    D=M
    M=M+D // M=256
    D=M
    M=M+D // M=512
    D=M
    M=M+D // M=1024
    D=M
    M=M+D // M=2048
    D=M
    M=M+D // M=4096
    D=M
    M=M+D // M=8192

    @SCREEN
    D=A

// int16 *end_of_screen_addr = SCREEND + 0x2000;
    @v8k
    D=D+M
    @end_of_screen_addr 
    M=D


(EVENT_LOOP)
// while (True) {
    @KBD
    D=M

// int16 color;
// if (key_pressed) {
//    color = 0b1111111111111111;
// }
// else {
//     color = 0;   
// }
// color_screen(color);
    
    @SET_BLACK
    D;JNE
    @color
    M=0
    @COLOR_SCREEN
    0;JMP
(SET_BLACK)
    @color
    M=-1

(COLOR_SCREEN)
// int16 *current_word = SCRREN;
    @SCREEN
    D=A
    @current_word_addr
    M=D

(COLOR_WORD)
// while(True) {
//  *current_word = color;
    @color
    D=M
    @current_word_addr
    A=M
    M=D
    
//  current_word++;
    @current_word_addr
    M=M+1

//  if current_word > SCREEN_END {
//      break;   
//  }
// }
    @end_of_screen_addr
    D=M
    @current_word_addr
    D=D-M
    @COLOR_WORD
    D;JGT
    @EVENT_LOOP
    0;JMP