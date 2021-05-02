use rand::Rng;

use toy_rsa::*;

#[test]
fn test_exp() {
    assert_eq!(EXP, 65_537);
}

#[test]
fn test_rsa_example() {
    let msg = 12345;
    let (p, q) = (0xed23e6cd, 0xf050a04d);
    let cmsg = encrypt(p as u64 * q as u64, msg);
    let pmsg = decrypt((p, q), cmsg);
    assert_eq!(msg, pmsg);
}

#[test]
fn test_rsa_random() {
    let mut rng = rand::thread_rng();
    for _ in 0..100 {
        let plain = rng.gen_range(0..u32::max_value());
        let (p, q) = genkey();
        let cipher = encrypt(p as u64 * q as u64, plain);
        let decrypted = decrypt((p, q), cipher);
        assert_eq!(plain, decrypted);
    }
}
