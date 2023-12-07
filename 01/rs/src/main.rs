use std::fs;

fn parse_line(line: &str) -> (i32, i32) {
    let mut first_num = -1;
    let mut last_num = -1;

    for c in line.chars() {
        if c.is_digit(10) {
            if let Some(digit) = c.to_digit(10) {
                last_num = digit as i32;
                if first_num == -1 {
                    first_num = last_num;
                }
            }
            
        }
    }
    return (first_num, last_num);
}

fn combine_digits(num_pairs: (i32, i32)) -> i32 {
    let first = num_pairs.0.to_string();
    let second = num_pairs.1.to_string();
    let combined = first + &second;
    return combined.parse::<i32>().unwrap();
}

fn main() {
    let contents = fs::read_to_string("input.txt").expect("Something went wrong reading the file");
    let lines = contents.split("\n").map(|line| line.trim()).filter(|line| !line.is_empty());

    let num_pairs = lines.map(|line| parse_line(line)).collect::<Vec<(i32, i32)>>();
    let combined = num_pairs.iter().map(|pair| combine_digits(*pair)).collect::<Vec<i32>>();
    let sum = combined.iter().sum::<i32>();
    println!("Sum: {}", sum);
}
