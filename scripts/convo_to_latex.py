def process_conversation_log(input_file, output_file):
    try:
        # Read the contents of the input file
        with open(input_file, "r") as file:
            content = file.read()

        # Replace unwanted characters
        content = content.replace("[91m", "").replace("[39m", "")

        # Wrap the content in the lstlisting environment
        latex_content = "\\begin{lstlisting}\n" + content + "\n\\end{lstlisting}"

        # Write the modified content to the output file
        with open(output_file, "w") as file:
            file.write(latex_content)

        print(f"File processed successfully. Output saved to '{output_file}'")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    process_conversation_log("./scripts/input.txt", "./scripts/output.tex")
