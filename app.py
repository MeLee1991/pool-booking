# =========================
# 1. DATABASE HELPERS
# =========================
USERS_FILE = "users.csv"
BOOKINGS_FILE = "bookings.csv"

def load_data(file, columns):
    if os.path.exists(file):
        # dtype=str forces Pandas to treat passwords like "1234" as text, not math numbers!
        return pd.read_csv(file, dtype=str) 
    return pd.DataFrame(columns=columns)

def save_data(df, file):
    df.to_csv(file, index=False)

# Initialize data
users = load_data(USERS_FILE, ["Email", "Name", "Password", "Role"])
bookings = load_data(BOOKINGS_FILE, ["User", "Name", "Date", "Table", "Time"])

# ... Keep your SESSION STATE and CSS exactly the same ...

# =========================
# 4. LOGIN & AUTH FLOW
# =========================
if st.session_state.user is None:
    st.title("🎱 Pool Booking")
    st.subheader("Login or Register")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        email_in = st.text_input("Email", key="log_email").strip().lower()
        pass_in = st.text_input("Password", type="password", key="log_pass").strip()
        
        if st.button("Log In", use_container_width=True):
            # We force both the dataframe columns and the inputs to be strings just to be 100% safe
            match = users[(users["Email"].astype(str) == email_in) & (users["Password"].astype(str) == pass_in)]
            
            if not match.empty:
                st.session_state.user = match.iloc[0]["Email"]
                st.session_state.name = match.iloc[0]["Name"]
                st.session_state.role = match.iloc[0]["Role"]
                st.rerun()
            else:
                st.error("Invalid credentials. Please try again.")

    with tab2:
        new_email = st.text_input("New Email", key="reg_email").strip().lower()
        new_name = st.text_input("Full Name", key="reg_name").strip()
        new_pass = st.text_input("New Password", type="password", key="reg_pass").strip()
        
        if st.button("Register", use_container_width=True):
            if new_email and new_name and new_pass:
                # Check if email already exists
                if not users[users["Email"].astype(str) == new_email].empty:
                    st.warning("This email is already registered!")
                else:
                    assigned_role = "admin" if users.empty else "user"
                    new_row = pd.DataFrame([[new_email, new_name, new_pass, assigned_role]], columns=users.columns)
                    users = pd.concat([users, new_row], ignore_index=True)
                    save_data(users, USERS_FILE)
                    st.success("Registered! You can now log in.")
            else:
                st.warning("Please fill in all fields.")
    st.stop()
