use kwindex::*;

#[test]
fn test_basics() {
    let kwindex = KWIndex::new();
    assert!(kwindex.is_empty());
    let kwindex = KWIndex::new().extend_from_text("Hello world.");
    assert_eq!(2, kwindex.len());
    assert_eq!(1, kwindex.count_matches("world"));

    let kwindex = KWIndex::new().extend_from_text("Can't stop this!");
    assert_eq!(2, kwindex.len());
}

#[test]
fn test_punctuation() {
    let kwindex = KWIndex::new().extend_from_text("It ain't over until it ain't, over.");
    assert_eq!(5, kwindex.len());
    assert_eq!(0, kwindex.count_matches("ain't"));
}

#[test]
fn test_count_matches() {
    let kwindex = KWIndex::new();
    assert_eq!(0, kwindex.count_matches("what"));

    let kwindex = KWIndex::new().extend_from_text("b b b-banana b");
    assert_eq!(0, kwindex.count_matches("banana"));
    assert_eq!(3, kwindex.count_matches("b"));

    let kwindex = KWIndex::new().extend_from_text("Hello world, world!");
    assert_eq!(2, kwindex.count_matches("world"));
}

#[test]
fn test_nth_uppercase() {
    let kwindex = KWIndex::new().extend_from_text("I am NOT the WALRUS");

    assert_eq!(5, kwindex.len());

    assert_eq!(Some("I"), kwindex.nth_uppercase(0));
    assert_eq!(Some("NOT"), kwindex.nth_uppercase(1));
    assert_eq!(Some("WALRUS"), kwindex.nth_uppercase(2));
}

#[test]
fn test_nth_uppercase_refs() {
    let s = "I am NOT the WALRUS";
    let words: Vec<&str> = s.split(char::is_whitespace).collect();

    let kwindex = KWIndex::new().extend_from_text("I am NOT the WALRUS");

    assert!(std::ptr::eq(kwindex.nth_uppercase(0).unwrap(), words[0]));
    assert!(std::ptr::eq(kwindex.nth_uppercase(1).unwrap(), words[2]));
    assert!(std::ptr::eq(kwindex.nth_uppercase(2).unwrap(), words[4]));
}
