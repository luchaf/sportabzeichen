import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# ---------- Helper Functions ----------

def time_to_seconds(time_str):
    """Convert a string formatted as MM:SS into total seconds."""
    try:
        minutes, seconds = time_str.split(":")
        return int(minutes) * 60 + int(seconds)
    except Exception as e:
        st.error(f"Time conversion error for {time_str}: {e}")
        return None

def get_level(result, thresh, lower_is_better=True):
    """
    Compare the user's result with the thresholds.
    For lower-is-better disciplines, a result less than or equal to a threshold qualifies.
    For higher-is-better disciplines, a result greater than or equal qualifies.
    """
    if lower_is_better:
        if result <= thresh["Gold"]:
            return "Gold"
        elif result <= thresh["Silber"]:
            return "Silber"
        elif result <= thresh["Bronze"]:
            return "Bronze"
        else:
            return "Below Bronze"
    else:
        if result >= thresh["Gold"]:
            return "Gold"
        elif result >= thresh["Silber"]:
            return "Silber"
        elif result >= thresh["Bronze"]:
            return "Bronze"
        else:
            return "Below Bronze"

# ---------- Benchmark Dictionaries ----------
# Times for running events are stored in "MM:SS" and then converted to seconds.
running_3000 = {
    "18–19": {"Bronze": time_to_seconds("17:50"), "Silber": time_to_seconds("15:50"), "Gold": time_to_seconds("13:50")},
    "20–24": {"Bronze": time_to_seconds("17:20"), "Silber": time_to_seconds("15:20"), "Gold": time_to_seconds("13:20")},
    "25–29": {"Bronze": time_to_seconds("17:40"), "Silber": time_to_seconds("15:40"), "Gold": time_to_seconds("13:40")},
    "30–34": {"Bronze": time_to_seconds("18:30"), "Silber": time_to_seconds("16:30"), "Gold": time_to_seconds("14:30")},
    "35–39": {"Bronze": time_to_seconds("19:50"), "Silber": time_to_seconds("17:20"), "Gold": time_to_seconds("15:00")},
    "40–44": {"Bronze": time_to_seconds("21:00"), "Silber": time_to_seconds("18:30"), "Gold": time_to_seconds("15:50")},
    "45–49": {"Bronze": time_to_seconds("22:10"), "Silber": time_to_seconds("19:30"), "Gold": time_to_seconds("16:30")},
    "50–54": {"Bronze": time_to_seconds("23:20"), "Silber": time_to_seconds("20:20"), "Gold": time_to_seconds("17:20")},
    "55–59": {"Bronze": time_to_seconds("23:50"), "Silber": time_to_seconds("20:50"), "Gold": time_to_seconds("17:50")},
    "60–64": {"Bronze": time_to_seconds("24:30"), "Silber": time_to_seconds("21:30"), "Gold": time_to_seconds("18:30")},
    "65–69": {"Bronze": time_to_seconds("25:00"), "Silber": time_to_seconds("22:00"), "Gold": time_to_seconds("19:00")},
    "70–74": {"Bronze": time_to_seconds("25:20"), "Silber": time_to_seconds("22:20"), "Gold": time_to_seconds("19:20")},
    "75–79": {"Bronze": time_to_seconds("26:00"), "Silber": time_to_seconds("23:00"), "Gold": time_to_seconds("20:00")},
    "80–84": {"Bronze": time_to_seconds("26:30"), "Silber": time_to_seconds("23:30"), "Gold": time_to_seconds("20:30")},
    "85–89": {"Bronze": time_to_seconds("27:30"), "Silber": time_to_seconds("24:30"), "Gold": time_to_seconds("21:30")},
    "ab90":  {"Bronze": time_to_seconds("29:50"), "Silber": time_to_seconds("26:50"), "Gold": time_to_seconds("23:50")}
}

running_10km = {
    "18–19": {"Bronze": time_to_seconds("63:20"), "Silber": time_to_seconds("57:20"), "Gold": time_to_seconds("51:20")},
    "20–24": {"Bronze": time_to_seconds("62:30"), "Silber": time_to_seconds("56:30"), "Gold": time_to_seconds("50:00")},
    "25–29": {"Bronze": time_to_seconds("66:00"), "Silber": time_to_seconds("59:20"), "Gold": time_to_seconds("52:00")},
    "30–34": {"Bronze": time_to_seconds("69:40"), "Silber": time_to_seconds("61:10"), "Gold": time_to_seconds("54:50")},
    "35–39": {"Bronze": time_to_seconds("74:10"), "Silber": time_to_seconds("65:30"), "Gold": time_to_seconds("56:50")},
    "40–44": {"Bronze": time_to_seconds("78:50"), "Silber": time_to_seconds("69:30"), "Gold": time_to_seconds("60:10")},
    "45–49": {"Bronze": time_to_seconds("83:40"), "Silber": time_to_seconds("73:10"), "Gold": time_to_seconds("63:30")},
    "50–54": {"Bronze": time_to_seconds("88:20"), "Silber": time_to_seconds("76:40"), "Gold": time_to_seconds("65:30")},
    "55–59": {"Bronze": time_to_seconds("91:30"), "Silber": time_to_seconds("79:40"), "Gold": time_to_seconds("67:40")},
    "60–64": {"Bronze": time_to_seconds("94:40"), "Silber": time_to_seconds("82:40"), "Gold": time_to_seconds("70:40")},
    "65–69": {"Bronze": time_to_seconds("98:00"), "Silber": time_to_seconds("86:00"), "Gold": time_to_seconds("74:00")},
    "70–74": {"Bronze": time_to_seconds("102:10"), "Silber": time_to_seconds("90:10"), "Gold": time_to_seconds("78:10")},
    "75–79": {"Bronze": time_to_seconds("107:20"), "Silber": time_to_seconds("95:20"), "Gold": time_to_seconds("83:20")},
    "80–84": {"Bronze": time_to_seconds("113:10"), "Silber": time_to_seconds("101:10"), "Gold": time_to_seconds("89:10")},
    "85–89": {"Bronze": time_to_seconds("120:10"), "Silber": time_to_seconds("108:10"), "Gold": time_to_seconds("96:10")},
    "ab90":  {"Bronze": time_to_seconds("127:40"), "Silber": time_to_seconds("115:40"), "Gold": time_to_seconds("103:40")}
}

# For throwing events, thresholds are stored as float values (in meters)
med_ball = {
    "18–19": {"Bronze": 11.00, "Silber": 13.00, "Gold": 14.00},
    "20–24": {"Bronze": 11.00, "Silber": 13.50, "Gold": 14.50},
    "25–29": {"Bronze": 10.50, "Silber": 13.00, "Gold": 14.50},
    "30–34": {"Bronze": 10.00, "Silber": 13.00, "Gold": 14.00},
    "35–39": {"Bronze": 9.50,  "Silber": 12.50, "Gold": 14.00},
    "40–44": {"Bronze": 9.00,  "Silber": 12.00, "Gold": 13.50},
    "45–49": {"Bronze": 8.00,  "Silber": 11.50, "Gold": 13.50},
    "50–54": {"Bronze": 7.50,  "Silber": 11.00, "Gold": 13.00},
    "55–59": {"Bronze": 7.00,  "Silber": 10.50, "Gold": 12.50},
    "60–64": {"Bronze": 6.50,  "Silber": 10.00, "Gold": 12.50},
    "65–69": {"Bronze": 6.00,  "Silber": 9.50,  "Gold": 11.50},
    "70–74": {"Bronze": 6.00,  "Silber": 9.00,  "Gold": 10.50},
    "75–79": {"Bronze": 5.50,  "Silber": 8.00,  "Gold": 9.50},
    "80–84": {"Bronze": 5.00,  "Silber": 7.50,  "Gold": 9.00},
    "85–89": {"Bronze": 4.50,  "Silber": 6.50,  "Gold": 8.00},
    "ab90":  {"Bronze": 4.00,  "Silber": 5.50,  "Gold": 8.00}
}

kugelstossen = {
    "18–19": {"Bronze": 7.75, "Silber": 8.25, "Gold": 8.75},
    "20–24": {"Bronze": 7.75, "Silber": 8.50, "Gold": 9.00},
    "25–29": {"Bronze": 7.50, "Silber": 8.25, "Gold": 8.75},
    "30–34": {"Bronze": 7.00, "Silber": 7.75, "Gold": 8.25},
    "35–39": {"Bronze": 6.75, "Silber": 7.25, "Gold": 8.00},
    "40–44": {"Bronze": 6.25, "Silber": 7.00, "Gold": 7.75},
    "45–49": {"Bronze": 6.00, "Silber": 6.75, "Gold": 7.50},
    "50–54": {"Bronze": 5.50, "Silber": 6.75, "Gold": 7.50},
    "55–59": {"Bronze": 5.00, "Silber": 5.75, "Gold": 6.50},
    "60–64": {"Bronze": 4.75, "Silber": 5.50, "Gold": 6.25},
    "65–69": {"Bronze": 4.50, "Silber": 5.25, "Gold": 6.15},
    "70–74": {"Bronze": 4.25, "Silber": 5.00, "Gold": 6.00},
    "75–79": {"Bronze": 4.25, "Silber": 5.25, "Gold": 6.25},
    "80–84": {"Bronze": 4.00, "Silber": 5.00, "Gold": 5.75},
    "85–89": {"Bronze": 3.75, "Silber": 4.50, "Gold": 5.50},
    "ab90":  {"Bronze": 3.25, "Silber": 4.25, "Gold": 5.00}
}

# Map discipline names to our benchmark data and indicate whether lower is better
benchmarks = {
    "3.000 m Lauf": {"data": running_3000, "lower_is_better": True, "unit": "seconds"},
    "10 km Lauf":   {"data": running_10km,   "lower_is_better": True, "unit": "seconds"},
    "Medizinball (2kg)": {"data": med_ball,       "lower_is_better": False, "unit": "meters"},
    "Kugelstoßen":       {"data": kugelstossen,   "lower_is_better": False, "unit": "meters"}
}

# Define the age groups
age_groups = ["18–19", "20–24", "25–29", "30–34", "35–39", "40–44",
              "45–49", "50–54", "55–59", "60–64", "65–69", "70–74",
              "75–79", "80–84", "85–89", "ab90"]

# ---------- Google Sheets Connection ----------
# Create a GSheets connection using the Streamlit connection API.
conn = st.connection("gsheets", type=GSheetsConnection)

# Define the worksheet name for storing performance results.
worksheet_name = "performance_results"

# Read the current data from the worksheet.
df = conn.read(worksheet=worksheet_name)
# If the sheet is empty, create an empty DataFrame with the required columns.
if df is None or df.empty:
    df = pd.DataFrame(columns=["Name", "Discipline", "Age Group", "Result", "Achieved Level", "Timestamp"])

# ---------- App Layout with Tabs ----------
tabs = st.tabs(["Online Form", "Recorded Performances"])

with tabs[0]:
    st.header("Enter Your Performance Data")
    
    # Initialize session state variables if not already present.
    if "data_written" not in st.session_state:
        st.session_state["data_written"] = False
    if "name" not in st.session_state:
        st.session_state["name"] = ""
    if "discipline" not in st.session_state:
        st.session_state["discipline"] = list(benchmarks.keys())[0]
    if "age_group" not in st.session_state:
        st.session_state["age_group"] = age_groups[0]
    if "result" not in st.session_state:
        st.session_state["result"] = 0.0

    if st.session_state["data_written"]:
        st.success("Performance data saved! Enter another record?")
        if st.button("Add Another Record"):
            st.session_state["data_written"] = False
            st.experimental_rerun()
    else:
        # Form Widgets
        name = st.text_input("Name", value=st.session_state["name"], key="name")
        discipline = st.selectbox("Discipline", list(benchmarks.keys()),
                                  index=list(benchmarks.keys()).index(st.session_state["discipline"]),
                                  key="discipline")
        age_group = st.selectbox("Age Group", age_groups, key="age_group")
        unit = benchmarks[discipline]["unit"]
        if benchmarks[discipline]["lower_is_better"]:
            st.info(f"For {discipline}, a lower value (in {unit}) is better.")
        else:
            st.info(f"For {discipline}, a higher value (in {unit}) is better.")
        result = st.number_input(f"Your Result ({unit})", min_value=0.0, value=st.session_state["result"], step=0.1, key="result")
        
        if st.button("Submit Performance"):
            # Retrieve benchmark thresholds for the chosen discipline and age group.
            bench_data = benchmarks[discipline]["data"][age_group]
            lower_is_better = benchmarks[discipline]["lower_is_better"]
            achieved_level = get_level(result, bench_data, lower_is_better)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Create a new record as a dictionary.
            new_record = {
                "Name": name,
                "Discipline": discipline,
                "Age Group": age_group,
                "Result": result,
                "Achieved Level": achieved_level,
                "Timestamp": timestamp
            }
            
            # Append the new record to the existing DataFrame.
            updated_df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
            # Update the Google Sheet.
            conn.update(worksheet=worksheet_name, data=updated_df)
            
            st.session_state["data_written"] = True
            st.experimental_rerun()

    # Display benchmark details for the selected discipline and age group.
    st.subheader(f"Benchmark for {discipline} ({age_group})")
    bench_info = benchmarks[discipline]["data"][age_group]
    if benchmarks[discipline]["lower_is_better"]:
        st.write(f"Gold: {bench_info['Gold']} {unit} or less")
        st.write(f"Silber: {bench_info['Silber']} {unit} or less")
        st.write(f"Bronze: {bench_info['Bronze']} {unit} or less")
    else:
        st.write(f"Bronze: {bench_info['Bronze']} {unit} or more")
        st.write(f"Silber: {bench_info['Silber']} {unit} or more")
        st.write(f"Gold: {bench_info['Gold']} {unit} or more")

with tabs[1]:
    st.header("Recorded Performance Data")
    # Refresh the data from the Google Sheet
    df_updated = conn.read(worksheet=worksheet_name)
    if df_updated is None or df_updated.empty:
        st.write("No performance records found yet.")
    else:
        st.dataframe(df_updated)
        csv_data = df_updated.to_csv(index=False).encode("utf-8")
        st.download_button("Download Data as CSV", data=csv_data, file_name="performance_results.csv")
