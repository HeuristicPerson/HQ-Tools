Clean vs Dirty Hashes
=====================

**TODO:** Maybe it's better to move this document to hqlib documentation because it doesn't much sense here.

1. What's inside a file
-----------------------

Lets start by the beginning... a computer file stores certain amount of data in digital format, which basically means
they are a long string of zeros (0) and ones (1):

    0110101010100010110110101110101011101011101110111110111...
    
Typically, they are split in groups of eight:
    
    01101010 10100010 11011010 11101010 11101011 10111011 1110111 ...
    
In the above example we have seven groups of eight zeros and ones (eight bits) that represent 7 numbers in binary
format. We can convert them to decimal format (using 0, 1, 2, 3, 4, 5, 6, 7, 8, and 9 characters), the normal way we use
to handle numbers (an 8 bit binary number is a number between 0 and 255 in decimal format):

    106 162 218 234 235 187 119 ...
    
Or we can also convert them to hexadecimal format (using 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, A, B, C, D, E, and F characters)
format which is the "standard" method when working with computers:

    6A A2 DA EA EB BB 77 ...
    
Remember, those numbers represent the same amounts in different formats:

         binary 01101010 10100010 11011010 11101010 11101011 10111011 1110111 ...
        decimal      106      162      218      234      235      187     119 ...
    hexadecimal       6A       A2       DA       EA       EB       BB      77 ...


2. How to check the content of a file
-------------------------------------

Now that we know that inside the file we just have zeros and ones that typically are put together in groups of 8 and
written in hex format. How can we check that two files are different or equal? Easy answer... comparing the numbers one
by one. `AA BB CC DD EE` and `AA 22 CC DD EE` are different because in the second position we have `BB` in the first
"file" and `22` in the second one.
  
But the simple method of comparing each number has a big caveat: you need to have BOTH files to compare them and reduces
the field of application of the comparison. For example, you cannot create a database of verified files. Instead, your
database would actually contain the verified files itself.

To solve that problem, the hash algorithms were created. Basically, they take the data contained in the file (the long
long chain of zeros and ones) and they generate a much shorter number that **represents** the file. Imagine, is like if
your telephone number were a representation of you as an human being. Of course, your telephone number **is not** you,
but **represents** or **identifies** you. But if you and I have different telephone numbers, we may be different human
beings. And the telephone number is short, you can send it by email, you can tell it to another person, you can store
it without actually storing the person (I think it's called kidnapping). If "your" john and "my" john have different
telephone numbers is because they are not the human beings. PERFECT!!!

(forget the case where a person has TWO different telephone numbers, hashing algorithms are surjective. It means that
every file have one and just one hash. It also means something else... read the next paragraph.)
 
Not that fast... You may noticed the first problem that hashing algorithms have to face. They need to be simple, small
and fast... but on the other hand they need to be complex in order to avoid collisions as much as possible. A collision
is when two files are different in fact but they have the same hash. Back to the example, imagine two different people
having the same telephone number... problems everywhere.

How the hashing algorithms deal with collisions? I like to say that by "brute force" or being as complicated and
generating a hash as long **as needed**. Imagine one very simple hash mechanism that makes the sum of the numbers in the
original file:

    Data: 155 23 47 -> Hash: 225
    Data: 107 99 19 -> Hash: 225
      
So we found a collision, let's make something more complex: I'm going to sum just the last cypher of each number:

    Data: 15(5) 2(3) 4(7) -> Hash: 15
    Data: 10(7) 9(9) 1(9) -> Hash: 25
    
Of course this new hash mechanism is not perfect, but it seems to be a bit (just a bit) better (at least for this
particular example).

So, to sum it up:

* Now you know what's a hash algorithm (or mechanism)
* You know there are many different hashing mechanisms
* The hash of a file is NOT the file, but a shorter (smaller) identification of a file
* Unfortunately the caveat of hashing algorithms is we can have collisions: different file content can generate the same
  hash.
* Because hashes are smaller than the actual data, you can compare two files without actually having them by simply
  comparing their hashes. And you can store the hashes too without having the files.
  
  
3. Real-World hashing mechanisms
--------------------------------

Let's go one step further to see which are the most common used hashing algorithms out there. They are **CRC32**,
**MD5**, and **SHA1**. The probability of having a collision between two particular files is calculated using this
formula:

    P(collision) = 1 / 16^n
    
Where `n` is 8 for CRC32, 32 for MD5, and 40 for SHA1. Really low in any case... but not as low if you take into
consideration the [Birthday Problem](http://www.wikiwand.com/en/Birthday_problem):

    P(collision) = 1 - e ^(-n^2 / 2 * H)
     
Or:

    P(collision) = 1 - e ^ (-n(n-1) / 2 * H)
