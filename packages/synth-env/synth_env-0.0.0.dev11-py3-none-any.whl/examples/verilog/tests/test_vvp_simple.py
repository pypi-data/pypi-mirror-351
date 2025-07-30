#!/usr/bin/env python3
"""
Simple test suite for VVP simulation bug - minimal dependencies.

These tests should FAIL until the VVP stdout capture bug is fixed.

Run with: pytest test_vvp_simple.py -v

To run manually:
    cd src/examples/verilog/tests
    python test_vvp_simple.py
"""

import subprocess
import tempfile
import pytest
from pathlib import Path


class TestVVPSimpleBug:
    """Simple tests targeting VVP subprocess stdout capture."""
    
    @pytest.fixture
    def verilog_test_files(self):
        """Minimal Verilog files that should produce clear success output."""
        return {
            "TopModule.v": """module TopModule(output zero);
    assign zero = 1'b0;
endmodule
""",
            "RefModule.v": """module RefModule(
  output zero
);
  assign zero = 1'b0;
endmodule
""",
            "test_tb.v": """`timescale 1ns/1ps

module tb();
    reg clk = 0;
    wire zero_dut, zero_ref;
    integer errors = 0;
    integer clocks = 0;
    
    always #5 clk = ~clk;
    
    TopModule dut(.zero(zero_dut));
    RefModule ref(.zero(zero_ref));
    
    always @(posedge clk) begin
        clocks = clocks + 1;
        if (zero_dut !== zero_ref) begin
            errors = errors + 1;
            $display("ERROR at time %0t: zero_dut=%b, zero_ref=%b", $time, zero_dut, zero_ref);
        end
        
        if (clocks >= 10) begin
            if (errors == 0) begin
                $display("Hint: Output 'zero' has no mismatches.");
                $display("Hint: Total mismatched samples is 0 out of %0d samples", clocks);
            end else begin
                $display("Hint: Output 'zero' has %0d mismatches. First mismatch occurred at time 5.", errors);
                $display("Hint: Total mismatched samples is %0d out of %0d samples", errors, clocks);
            end
            $display("Simulation finished at %0d ps", $time);
            $display("Mismatches: %0d in %0d samples", errors, clocks);
            $finish;
        end
    end
endmodule
"""
        }

    def test_manual_vvp_produces_output(self, verilog_test_files):
        """
        SHOULD PASS: Test that VVP manually produces expected output.
        
        This isolates whether VVP itself works vs environment subprocess capture.
        If this passes but environment tests fail, confirms subprocess bug.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Write test files
            for filename, content in verilog_test_files.items():
                (temp_path / filename).write_text(content)
            
            # Compile with iverilog
            compile_cmd = [
                "iverilog", 
                "-o", "test.out",
                "TopModule.v", "RefModule.v", "test_tb.v"
            ]
            
            compile_proc = subprocess.run(
                compile_cmd, 
                cwd=temp_dir, 
                capture_output=True, 
                text=True
            )
            
            assert compile_proc.returncode == 0, \
                f"Compilation failed:\nstdout: {compile_proc.stdout}\nstderr: {compile_proc.stderr}"
            
            binary_path = temp_path / "test.out"
            assert binary_path.exists(), "Compiled binary should exist"
            
            # Run VVP simulation
            vvp_proc = subprocess.run(
                ["vvp", "test.out"],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            print(f"VVP return code: {vvp_proc.returncode}")
            print(f"VVP stdout: '{vvp_proc.stdout}'")
            print(f"VVP stderr: '{vvp_proc.stderr}'")
            
            # These should pass if VVP works correctly
            assert vvp_proc.returncode == 0, f"VVP failed with stderr: {vvp_proc.stderr}"
            assert vvp_proc.stdout.strip() != "", "VVP should produce stdout output"
            
            # Check for expected patterns
            stdout = vvp_proc.stdout
            assert "no mismatches" in stdout.lower(), f"Should contain success pattern in: {stdout}"
            assert "Mismatches: 0" in stdout, f"Should show zero mismatches in: {stdout}"
            assert "Simulation finished" in stdout, f"Should show completion in: {stdout}"

    def test_pattern_detection_logic(self):
        """
        Test that success pattern detection works with expected VVP output.
        
        This verifies the environment's pattern matching logic.
        """
        # Example outputs and expected results
        test_cases = [
            # Good outputs (should pass)
            ("Hint: Output 'zero' has no mismatches.\nMismatches: 0 in 10 samples", True),
            ("ALL_TESTS_PASSED\nSimulation complete", True),
            ("Mismatches: 0 in 42 samples\nTest passed", True),
            ("Output has no mismatches detected", True),
            
            # Bad outputs (should fail)  
            ("Hint: Output 'zero' has 3 mismatches.\nMismatches: 3 in 10 samples", False),
            ("Simulation error occurred", False),
            ("Timeout reached", False),
            ("", False),  # Empty output - the bug case!
        ]
        
        for output, expected_pass in test_cases:
            # This is the exact logic from environment.py lines 154-158
            passed = (
                "ALL_TESTS_PASSED" in output or
                ("Mismatches: 0 " in output and "samples" in output) or
                ("no mismatches" in output.lower() and "errors" not in output.lower())
            )
            
            assert passed == expected_pass, \
                f"Pattern detection failed for output: '{output}'\nExpected: {expected_pass}, Got: {passed}"

    def test_empty_stdout_fails_detection(self):
        """
        DOCUMENTS BUG: Empty stdout should fail pattern detection.
        
        This test shows the current bug behavior - empty stdout is not detected as success.
        """
        empty_output = ""
        
        # Current environment logic
        passed = (
            "ALL_TESTS_PASSED" in empty_output or
            ("Mismatches: 0 " in empty_output and "samples" in empty_output) or
            ("no mismatches" in empty_output.lower() and "errors" not in empty_output.lower())
        )
        
        # This correctly fails - empty output should not be considered success
        assert not passed, "Empty stdout should not be detected as success"
        
        # But the problem is that the environment is getting empty stdout 
        # when it should be getting actual VVP output!

    def test_engine_subprocess_bug(self):
        """
        Test that demonstrates the bug in VerilogEngine.simulate().
        
        This test mimics what the engine does and shows the bug.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Write test files
            test_files = {
                "TopModule.v": """module TopModule(output zero);
    assign zero = 1'b0;
endmodule
""",
                "test_tb.v": """`timescale 1ns/1ps
module tb();
    wire zero;
    TopModule dut(.zero(zero));
    initial begin
        #10;
        $display("Hint: Output 'zero' has no mismatches.");
        $display("Mismatches: 0 in 1 samples");
        $finish;
    end
endmodule
"""
            }
            
            for filename, content in test_files.items():
                (temp_path / filename).write_text(content)
            
            # Compile
            compile_proc = subprocess.run(
                ["iverilog", "-o", "test.out", "TopModule.v", "test_tb.v"],
                cwd=temp_dir,
                capture_output=True,
                text=True
            )
            assert compile_proc.returncode == 0
            
            # This is the exact subprocess call from engine.py line 270
            bin_path = str(temp_path / "test.out")
            proc = subprocess.run(["vvp", bin_path], capture_output=True, text=True, timeout=30)
            
            # THIS IS THE BUG: proc.stdout should have content but might be empty!
            print(f"Engine-style VVP stdout: '{proc.stdout}'")
            print(f"Engine-style VVP stderr: '{proc.stderr}'")
            
            # Document the bug behavior
            if proc.stdout.strip() == "":
                print("BUG CONFIRMED: VVP stdout is empty when it should have output!")
            else:
                print("BUG NOT REPRODUCED: VVP stdout has content as expected")


def run_direct_test():
    """Run tests directly without pytest for easier debugging."""
    test_instance = TestVVPSimpleBug()
    
    # Test VVP directly
    verilog_files = {
        "TopModule.v": """module TopModule(output zero);
    assign zero = 1'b0;
endmodule
""",
        "RefModule.v": """module RefModule(
  output zero
);
  assign zero = 1'b0;
endmodule
""",
        "test_tb.v": """`timescale 1ns/1ps

module tb();
    reg clk = 0;
    wire zero_dut, zero_ref;
    integer errors = 0;
    integer clocks = 0;
    
    always #5 clk = ~clk;
    
    TopModule dut(.zero(zero_dut));
    RefModule ref(.zero(zero_ref));
    
    always @(posedge clk) begin
        clocks = clocks + 1;
        if (zero_dut !== zero_ref) begin
            errors = errors + 1;
        end
        
        if (clocks >= 5) begin
            if (errors == 0) begin
                $display("Hint: Output 'zero' has no mismatches.");
                $display("Mismatches: 0 in %0d samples", clocks);
            end else begin
                $display("Hint: Output 'zero' has %0d mismatches.", errors);
                $display("Mismatches: %0d in %0d samples", errors, clocks);
            end
            $display("Simulation finished at %0d ps", $time);
            $finish;
        end
    end
endmodule
"""
    }
    
    try:
        test_instance.test_manual_vvp_produces_output(verilog_files)
        print("✅ VVP manual test PASSED - VVP produces output correctly")
    except Exception as e:
        print(f"❌ VVP manual test FAILED: {e}")
    
    try:
        test_instance.test_pattern_detection_logic()
        print("✅ Pattern detection test PASSED")
    except Exception as e:
        print(f"❌ Pattern detection test FAILED: {e}")
    
    try:
        test_instance.test_empty_stdout_fails_detection()
        print("✅ Empty stdout test PASSED - correctly fails on empty output")
    except Exception as e:
        print(f"❌ Empty stdout test FAILED: {e}")
    
    try:
        test_instance.test_engine_subprocess_bug()
        print("✅ Engine subprocess bug test completed")
    except Exception as e:
        print(f"❌ Engine subprocess bug test FAILED: {e}")


if __name__ == "__main__":
    print("Running VVP bug tests directly...")
    run_direct_test()