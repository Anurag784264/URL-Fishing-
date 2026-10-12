"""
Master Launcher & Management Hub - PhishShield (Simplified Architecture)
Course: AI Systems and Applications (AISA) - Mini Project
Department of Computer Engineering and Technology

Run this script to interactively train the model, start the Streamlit web app,
or compile the academic PDF report and PowerPoint presentation.
"""

import os
import sys
import subprocess


def show_banner():
    print("=" * 72)
    print("      🛡️  PHISHSHIELD AI: PHISHING URL DETECTION (SIMPLIFIED)  🛡️")
    print("      Course: AI Systems and Applications (AISA) - Mini Project")
    print("      Department of Computer Engineering and Technology")
    print("=" * 72)


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    python_exec = sys.executable

    show_banner()
    print("\nSelect an action:")
    print("  [1] Launch Streamlit Web Application (app.py)")
    print("  [2] Train Machine Learning Model & Generate Plots (train_model.py)")
    print("  [3] Generate Academic PDF Project Report (generate_report_pdf.py)")
    print("  [4] Generate PowerPoint Presentation (generate_presentation_pptx.py)")
    print("  [5] Run Everything in Sequence (Train + Report + Presentation + Web App)")
    print("  [0] Exit")
    print("-" * 72)

    try:
        choice = input("Enter choice (0-5) [default 1]: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nExiting.")
        return

    if choice == "" or choice == "1":
        print("\n🚀 Launching Streamlit Web App...")
        cmd = [python_exec, "-m", "streamlit", "run", os.path.join(base_dir, "app.py")]
        subprocess.run(cmd)

    elif choice == "2":
        print("\n⚙️ Training Random Forest Model & generating evaluation charts...")
        cmd = [python_exec, os.path.join(base_dir, "train_model.py")]
        subprocess.run(cmd)

    elif choice == "3":
        print("\n📄 Generating Academic PDF Report...")
        cmd = [python_exec, os.path.join(base_dir, "generate_report_pdf.py")]
        subprocess.run(cmd)

    elif choice == "4":
        print("\n📊 Generating PowerPoint Presentation (12 Slides)...")
        cmd = [python_exec, os.path.join(base_dir, "generate_presentation_pptx.py")]
        subprocess.run(cmd)

    elif choice == "5":
        print("\n=== STEP 1: Retraining Model ===")
        subprocess.run([python_exec, os.path.join(base_dir, "train_model.py")])

        print("\n=== STEP 2: Compiling Academic PDF Report ===")
        subprocess.run([python_exec, os.path.join(base_dir, "generate_report_pdf.py")])

        print("\n=== STEP 3: Compiling PowerPoint Presentation ===")
        subprocess.run([python_exec, os.path.join(base_dir, "generate_presentation_pptx.py")])

        print("\n=== STEP 4: Launching Streamlit Web Application ===")
        subprocess.run([python_exec, "-m", "streamlit", "run", os.path.join(base_dir, "app.py")])

    elif choice == "0":
        print("\nGoodbye!")
    else:
        print("\nInvalid choice. Please run again and select a number from 0 to 5.")


if __name__ == "__main__":
    main()
