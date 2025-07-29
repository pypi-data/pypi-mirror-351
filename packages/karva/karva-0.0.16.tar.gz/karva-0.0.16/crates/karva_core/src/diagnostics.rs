use colored::{Color, Colorize};
use std::io::{self, Write};
use std::sync::{Arc, Mutex};
use std::time::Instant;

use crate::runner::RunnerResult;
use crate::test_result::{TestResult, TestResultError, TestResultFail, TestResultPass};

pub struct DiagnosticWriter {
    stdout: Arc<Mutex<Box<dyn Write + Send>>>,
    start_time: Instant,
    failed_tests: Vec<TestResultFail>,
    error_tests: Vec<TestResultError>,
}

impl Default for DiagnosticWriter {
    fn default() -> Self {
        Self::new(io::stdout())
    }
}

impl DiagnosticWriter {
    pub fn new(out: impl Write + Send + 'static) -> Self {
        Self {
            stdout: Arc::new(Mutex::new(Box::new(out))),
            start_time: Instant::now(),
            failed_tests: vec![],
            error_tests: vec![],
        }
    }

    fn acquire_stdout(&self) -> std::sync::MutexGuard<'_, Box<dyn Write + Send>> {
        self.stdout.lock().unwrap()
    }

    fn flush_stdout(&self, stdout: &mut std::sync::MutexGuard<'_, Box<dyn Write + Send>>) {
        let _ = stdout.flush();
    }

    pub fn test_started(&self, test_name: &str, file_path: &str) {
        tracing::info!("{} {} in {}", "Running".blue(), test_name, file_path,);
    }

    pub fn test_completed(&mut self, test: &TestResult) {
        match test {
            TestResult::Pass(test) => self.test_passed(test),
            TestResult::Fail(test) => self.test_failed(test),
            TestResult::Error(test) => self.test_error(test),
        }
    }

    fn test_passed(&self, _test: &TestResultPass) {
        self.log_test_result(Color::Green);
    }

    fn test_failed(&mut self, test: &TestResultFail) {
        self.log_test_result(Color::Red);
        self.failed_tests.push(test.clone());
    }

    fn test_error(&mut self, test: &TestResultError) {
        self.log_test_result(Color::Yellow);
        self.error_tests.push(test.clone());
    }

    fn log_test_result(&self, color: Color) {
        let mut stdout = self.acquire_stdout();
        let _ = write!(stdout, "{}", ".".color(color));
        self.flush_stdout(&mut stdout);
    }

    pub fn discovery_started(&self) {
        tracing::info!("{}", "Discovering tests...".blue());
    }

    pub fn discovery_completed(&self, count: usize) {
        let mut stdout = self.acquire_stdout();
        let _ = writeln!(
            stdout,
            "{} {} {}",
            "Discovered".blue(),
            count,
            "tests".blue()
        );
        self.flush_stdout(&mut stdout);
    }

    fn display_test_results(&self, stdout: &mut std::sync::MutexGuard<'_, Box<dyn Write + Send>>) {
        if !self.failed_tests.is_empty() {
            let _ = writeln!(stdout, "{}", "Failed tests:".red().bold());

            for test in self.failed_tests.iter() {
                let _ = writeln!(stdout, "{}", test.test.to_string().bold());
                if let Some(traceback) = &test.traceback {
                    let _ = writeln!(stdout, "{}", traceback);
                }
            }
        }
        if !self.error_tests.is_empty() {
            let _ = writeln!(stdout, "{}", "Error tests:".yellow().bold());

            for test in self.error_tests.iter() {
                let _ = writeln!(stdout, "{}", test.test.to_string().bold());
                let _ = writeln!(stdout, "{}", test.traceback);
            }
        }
    }

    pub fn finish(&self, runner_result: &RunnerResult) {
        let mut stdout = self.acquire_stdout();
        let stats = runner_result.stats();
        let total_duration = self.start_time.elapsed();

        fn maybe_log_test_count(
            stdout: &mut std::sync::MutexGuard<'_, Box<dyn Write + Send>>,
            label: &str,
            count: usize,
            color: Color,
        ) {
            if count > 0 {
                let _ = writeln!(
                    stdout,
                    "{} {}",
                    label.color(color),
                    count.to_string().color(color)
                );
            }
        }

        if stats.total_tests() > 0 {
            let _ = writeln!(stdout);
            self.display_test_results(&mut stdout);
            let _ = writeln!(stdout, "{}", "─────────────".bold());
            for (label, num, color) in [
                ("Passed tests:", stats.passed_tests(), Color::Green),
                ("Failed tests:", stats.failed_tests(), Color::Red),
                ("Error tests:", stats.error_tests(), Color::Yellow),
            ] {
                maybe_log_test_count(&mut stdout, label, num, color);
            }
            tracing::info!(
                "{} {}ms",
                "Total duration:".blue(),
                total_duration.as_millis()
            );
        }
        self.flush_stdout(&mut stdout);
    }
}

#[cfg(test)]
mod tests {
    use regex::Regex;
    use std::io::{self, Write};
    use std::sync::{Arc, Mutex};

    use super::*;
    use crate::discovery::DiscoveredTest;
    use crate::path::SystemPathBuf;
    use crate::project::Project;
    use crate::runner::RunnerResult;
    use crate::test_result::TestResult;

    #[derive(Clone, Debug)]
    struct SharedBufferWriter(Arc<Mutex<Vec<u8>>>);

    impl Write for SharedBufferWriter {
        fn write(&mut self, buf: &[u8]) -> io::Result<usize> {
            let mut inner = self.0.lock().unwrap();
            inner.extend_from_slice(buf);
            Ok(buf.len())
        }
        fn flush(&mut self) -> io::Result<()> {
            Ok(())
        }
    }

    fn strip_ansi_codes(s: &str) -> String {
        let re = Regex::new(r"\x1b\[[0-9;]*m").unwrap();
        re.replace_all(s, "").to_string()
    }

    fn create_test_writer() -> (DiagnosticWriter, Arc<Mutex<Vec<u8>>>) {
        let buffer = Arc::new(Mutex::new(Vec::new()));
        let writer = DiagnosticWriter::new(SharedBufferWriter(buffer.clone()));
        (writer, buffer)
    }

    fn get_project() -> Project {
        Project::new(SystemPathBuf::from("tests/"), vec![], "test".to_string())
    }

    fn get_discovered_test() -> DiscoveredTest {
        let temp_dir = tempfile::tempdir().unwrap();
        let file_path = temp_dir.path().join("test.py");
        std::fs::write(&file_path, "def test_name():\n    assert True\n").unwrap();

        let function_def =
            crate::discovery::visitor::function_definitions(file_path.into(), &get_project())
                .into_iter()
                .next()
                .unwrap();

        DiscoveredTest::new("test.py".to_string(), function_def)
    }

    fn get_test_result_pass() -> TestResult {
        TestResult::new_pass(get_discovered_test(), std::time::Duration::from_micros(100))
    }

    fn get_test_result_fail() -> TestResult {
        TestResult::new_fail(
            get_discovered_test(),
            Some(
                "File \"test.py\", line 3, in test_name\n  assert False, \"This test should fail\""
                    .to_string(),
            ),
            std::time::Duration::from_micros(100),
        )
    }

    fn get_test_result_error() -> TestResult {
        TestResult::new_error(
            get_discovered_test(),
            "File \"test.py\", line 3, in test_name\n  raise ValueError(\"This is an error\")"
                .to_string(),
            std::time::Duration::from_micros(100),
        )
    }

    #[test]
    fn test_test_passed() {
        let (mut writer, buffer) = create_test_writer();
        writer.test_completed(&get_test_result_pass());
        let output = String::from_utf8(buffer.lock().unwrap().clone()).unwrap();
        assert_eq!(output, ".".green().to_string());
    }

    #[test]
    fn test_test_failed() {
        let (mut writer, buffer) = create_test_writer();
        writer.test_completed(&get_test_result_fail());
        let output = String::from_utf8(buffer.lock().unwrap().clone()).unwrap();
        assert_eq!(output, ".".red().to_string());
    }

    #[test]
    fn test_test_error() {
        let (mut writer, buffer) = create_test_writer();
        writer.test_completed(&get_test_result_error());
        let output = String::from_utf8(buffer.lock().unwrap().clone()).unwrap();
        assert_eq!(output, ".".yellow().to_string());
    }

    #[test]
    fn test_discovery() {
        let (writer, buffer) = create_test_writer();
        writer.discovery_started();
        writer.discovery_completed(5);
        writer.finish(&RunnerResult::new(vec![]));
        let output = String::from_utf8(buffer.lock().unwrap().clone()).unwrap();
        let output = strip_ansi_codes(&output);
        let expected = "Discovered 5 tests\n";
        assert_eq!(output, expected);
    }

    #[test]
    fn test_finish_with_mixed_results() {
        let (mut writer, buffer) = create_test_writer();
        let test_results = vec![
            get_test_result_pass(),
            get_test_result_fail(),
            get_test_result_pass(),
        ];
        for test in &test_results {
            writer.test_completed(test);
        }
        let runner_result = RunnerResult::new(test_results);
        writer.finish(&runner_result);
        let output = String::from_utf8(buffer.lock().unwrap().clone()).unwrap();
        let output = strip_ansi_codes(&output);
        let expected = r#"...
Failed tests:
test.py::test_name
File "test.py", line 3, in test_name
  assert False, "This test should fail"
─────────────
Passed tests: 2
Failed tests: 1
"#;
        assert_eq!(output, expected);
    }

    #[test]
    fn test_finish_with_errors() {
        let (mut writer, buffer) = create_test_writer();
        let test_results = vec![
            get_test_result_pass(),
            get_test_result_error(),
            get_test_result_fail(),
        ];
        for test in &test_results {
            writer.test_completed(test);
        }
        let runner_result = RunnerResult::new(test_results);
        writer.finish(&runner_result);
        let output = String::from_utf8(buffer.lock().unwrap().clone()).unwrap();
        let output = strip_ansi_codes(&output);
        let expected = r#"...
Failed tests:
test.py::test_name
File "test.py", line 3, in test_name
  assert False, "This test should fail"
Error tests:
test.py::test_name
File "test.py", line 3, in test_name
  raise ValueError("This is an error")
─────────────
Passed tests: 1
Failed tests: 1
Error tests: 1
"#;
        assert_eq!(output, expected);
    }

    #[test]
    fn test_finish_with_zero_tests() {
        let (writer, buffer) = create_test_writer();
        let runner_result = RunnerResult::new(vec![]);
        writer.finish(&runner_result);
        let output = String::from_utf8(buffer.lock().unwrap().clone()).unwrap();
        assert_eq!(output, "");
    }

    #[test]
    fn test_finish_with_all_failed() {
        let (mut writer, buffer) = create_test_writer();
        let test_results = vec![get_test_result_fail(), get_test_result_fail()];
        for test in &test_results {
            writer.test_completed(test);
        }
        let runner_result = RunnerResult::new(test_results);
        writer.finish(&runner_result);
        let output = String::from_utf8(buffer.lock().unwrap().clone()).unwrap();
        let output = strip_ansi_codes(&output);
        let expected = r#"..
Failed tests:
test.py::test_name
File "test.py", line 3, in test_name
  assert False, "This test should fail"
test.py::test_name
File "test.py", line 3, in test_name
  assert False, "This test should fail"
─────────────
Failed tests: 2
"#;
        assert_eq!(output, expected);
    }

    #[test]
    fn test_finish_with_all_passed() {
        let (mut writer, buffer) = create_test_writer();
        let test_results = vec![get_test_result_pass(), get_test_result_pass()];
        for test in &test_results {
            writer.test_completed(test);
        }
        let runner_result = RunnerResult::new(test_results);
        writer.finish(&runner_result);
        let output = String::from_utf8(buffer.lock().unwrap().clone()).unwrap();
        let output = strip_ansi_codes(&output);
        let expected = r#"..
─────────────
Passed tests: 2
"#;
        assert_eq!(output, expected);
    }

    #[test]
    fn test_finish_with_all_error() {
        let (mut writer, buffer) = create_test_writer();
        let test_results = vec![get_test_result_error(), get_test_result_error()];
        for test in &test_results {
            writer.test_completed(test);
        }
        let runner_result = RunnerResult::new(test_results);
        writer.finish(&runner_result);
        let output = String::from_utf8(buffer.lock().unwrap().clone()).unwrap();
        let output = strip_ansi_codes(&output);
        let expected = r#"..
Error tests:
test.py::test_name
File "test.py", line 3, in test_name
  raise ValueError("This is an error")
test.py::test_name
File "test.py", line 3, in test_name
  raise ValueError("This is an error")
─────────────
Error tests: 2
"#;
        assert_eq!(output, expected);
    }
}
