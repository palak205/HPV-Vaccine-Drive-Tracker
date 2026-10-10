import streamlit as st
import pandas as pd
import glob
import streamlit.components.v1 as components

# Page configuration
st.set_page_config(
    page_title="CerviCare — HPV Drive Sites Finder",
    page_icon="🌸",
    layout="wide"
)
_, right = st.columns([4, 1])
with right:
    with st.popover("💬 Ask the chatbot", use_container_width=True):
        components.html(
            """
            <!-- Elfsight AI Chatbot | Untitled AI Chatbot -->
            <script src="https://elfsightcdn.com/platform.js" async></script>
            <div class="elfsight-app-24222ab6-c8fd-416d-a4f3-e509307f2ba4" data-elfsight-app-lazy></div>
            """,
            height=450,
        )
        

# Custom Styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');

html, body, [class*="css"], .stApp, .stMarkdown, button, input {
    font-family: 'Poppins', sans-serif !important;
}

/* Page title area */
h1, h2, h3, h4 { font-weight: 600; letter-spacing: -0.3px; }

/* Cards (bordered containers) */
[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 14px;
    border: 1px solid rgba(255, 255, 255, 0.12);
    background: rgba(255, 255, 255, 0.03);
    transition: transform .15s ease, border-color .15s ease;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: #ff4b8b;
    transform: translateY(-2px);
}

/* Metrics */
[data-testid="stMetricValue"] { color: #ff4b8b; font-weight: 700; }

/* Register button */
.stLinkButton a {
    background: #ff4b8b;
    color: white !important;
    border: none;
    border-radius: 10px;
    font-weight: 600;
}
.stLinkButton a:hover { background: #e63977; }
</style>
""", unsafe_allow_html=True) 

# Header Section
# Header Section
st.markdown("", unsafe_allow_html=True)
st.markdown("Empowering Prevention — Locate nearby HPV Vaccination Drive Sites & Schedule Appointments", unsafe_allow_html=True)

csv_files = glob.glob("*.csv")


if not csv_files:
 st.error("No CSV dataset found in the project folder! Please make sure your file is inside the hpv_tracker directory.")
 st.stop()

@st.cache_data
def load_data(file_path):
 return pd.read_csv(file_path)

data_path = csv_files[0]
df = load_data(data_path)
pincode_col = next((col for col in df.columns if 'pincode' in col.lower() or 'pin' in col.lower()), None)
if pincode_col:
 df[pincode_col] = df[pincode_col].astype(str).str.replace(r'.0$', '', regex=True).str.strip()
district_col = next((col for col in df.columns if 'district' in col.lower()), None)
name_col = next((col for col in df.columns if 'name' in col.lower() or 'site' in col.lower()), 'name')
type_col = next((col for col in df.columns if 'type' in col.lower()), 'type')
address_col = next((col for col in df.columns if 'address' in col.lower()), 'address')
date_col = next((col for col in df.columns if any(k in col.lower() for k in ['date', 'schedule', 'time', 'day'])), None)
link_col = next((col for col in df.columns if any(k in col.lower() for k in ['link', 'url', 'registration', 'web', 'site'])), None)
st.sidebar.header("🔍 Locate Drive Sites")

pincode_search = st.sidebar.text_input("Search by Pincode:", placeholder="e.g. 110001")

if pincode_col:
    all_pincodes = sorted([p for p in df[pincode_col].dropna().unique() if str(p).isdigit()])
    selected_pincodes = st.sidebar.multiselect("Filter by Pincode Dropdown:", options=all_pincodes)
else:
    selected_pincodes = []

if district_col:
 all_districts = sorted(df[district_col].dropna().unique().tolist())
 selected_districts = st.sidebar.multiselect("Filter by District:", options=all_districts)
else:
 selected_districts = []
filtered_df = df.copy()

if pincode_search and pincode_col:
 filtered_df = filtered_df[filtered_df[pincode_col].str.contains(pincode_search.strip(), case=False, na=False)]

if selected_pincodes and pincode_col:
 filtered_df = filtered_df[filtered_df[pincode_col].isin(selected_pincodes)]

if selected_districts and district_col:
 filtered_df = filtered_df[filtered_df[district_col].isin(selected_districts)]
col1, col2, col3 = st.columns(3)
col1.metric("Drive Sites Available", len(filtered_df))
col2.metric("Districts Covered", filtered_df[district_col].nunique() if district_col else "N/A")
col3.metric("Pincodes Represented", filtered_df[pincode_col].nunique() if pincode_col else "N/A")

st.divider()
st.subheader("📍 Vaccination Sites Directory")


from datetime import date

UWIN_URL = "https://uwin.mohfw.gov.in"   # fallback: please open it once to confirm it's correct

def clean_url(val):
    """Return a usable URL, or "" if the cell is empty or plain text."""
    if pd.isna(val):
        return ""
    s = str(val).strip()
    if not s or s.lower() == "nan" or " " in s:
        return ""
    if not s.startswith(("http://", "https://")):
        s = "https://" + s
    return s if "." in s else ""


def parse_dates(raw):
    out = set()
    for part in str(raw).split(";"):
        d = pd.to_datetime(part.strip(), errors="coerce")
        if pd.notna(d):
            out.add(d.date())
    return sorted(out)


def render_schedule(raw):
    dates = parse_dates(raw)
    if not dates:
        st.markdown("📅 **Schedule:** Not available")
        return

    today = date.today()
    upcoming = [d for d in dates if d >= today]

    if upcoming:
        nxt = upcoming[0]
        tag = " (today)" if nxt == today else ""
        st.markdown(f"📅 **Next session:** {nxt.strftime('%a, %d %b %Y')}{tag}")
    else:
        st.markdown("📅 **No upcoming sessions** (all listed dates have passed)")

    with st.expander(f"All dates · {len(upcoming)} upcoming of {len(dates)}"):
        for y, m in sorted({(d.year, d.month) for d in dates}):
            days = [d for d in dates if (d.year, d.month) == (y, m)]
            chips = "  ·  ".join(f"~~{d.day}~~" if d < today else f"**{d.day}**" for d in days)
            st.markdown(f"**{date(y, m, 1).strftime('%B %Y')}:**  {chips}")
        st.caption("Struck-through dates have already passed.")


def render_card(idx, row):
    site_name     = row.get(name_col, f"Drive Site #{idx + 1}")
    site_type     = row.get(type_col, "HPV Vaccination Site")
    site_address  = row.get(address_col, "Address details not available")
    site_pincode  = row.get(pincode_col, "N/A") if pincode_col else "N/A"
    site_district = row.get(district_col, "N/A") if district_col else "N/A"

    reg_url = clean_url(row.get(link_col)) if link_col else ""
    reg_url = reg_url or UWIN_URL

    with st.container(border=True):
        st.markdown(f"#### 📍 {site_name}")
        st.caption(f"{site_type}  ·  {site_district} ({site_pincode})")
        st.markdown(f"**Address:** {site_address}")
        render_schedule(row.get(date_col) if date_col else None)
        st.link_button("🔗 Register Now", reg_url, use_container_width=True)


# --- display section: NOT indented under the function ---
if filtered_df.empty:
    st.info("No vaccination drive sites match your criteria. Try adjusting your pincode or district.")
else:
    st.caption(f"Showing {len(filtered_df)} site(s)")
    rows = list(filtered_df.iterrows())
    for i in range(0, len(rows), 2):
        cols = st.columns(2)
        for col, (idx, row) in zip(cols, rows[i:i + 2]):
            with col:
                render_card(idx, row)
                
import streamlit.components.v1 as components

_, right = st.columns([4, 1])
with right:
    with st.popover("💬 Ask the chatbot", use_container_width=True):
        components.html(
            """
            <!-- Elfsight AI Chatbot | Untitled AI Chatbot -->
            <script src="https://elfsightcdn.com/platform.js" async></script>
            <div class="elfsight-app-24222ab6-c8fd-416d-a4f3-e509307f2ba4" data-elfsight-app-lazy></div>
            """,
            height=450,
        )

                