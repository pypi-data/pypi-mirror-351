fn main() -> std::io::Result<()> {
    println!("cargo::rerun-if-changed=pyproject.toml");

    // Read pyproject.toml to expose our version to the Rust extension
    let pyproject = std::fs::read_to_string("pyproject.toml")?
        .parse::<toml::Table>()
        .expect("pyproject.toml is valid toml");
    let version = pyproject
        .get("project")
        .and_then(|p| p.as_table())
        .and_then(|p| p.get("version"))
        .and_then(|v| v.as_str())
        .expect("version field is present in pyproject.toml");
    println!("cargo::rustc-env=PACKAGE_VERSION={}", version);

    // Figure out which Python version we're building for
    pyo3_build_config::use_pyo3_cfgs();

    Ok(())
}
