def post_install_message():
    print("""
*** IMPORTANT ***
If vp_prepare and vp_fig are not found, please add this to your ~/.bash_profile or ~/.bashrc:

    export PATH="$PATH:$(python3 -m site --user-base)/bin"

Then restart your terminal or run `source ~/.bash_profile` (or `source ~/.bashrc`).

""")
