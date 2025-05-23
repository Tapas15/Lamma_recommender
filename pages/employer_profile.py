import streamlit as st
import requests
import json
import pandas as pd
import re
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"

# Check authentication
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Please login to access this page")
    st.stop()

if st.session_state.user_type != "employer":
    st.warning("This page is only available for employers")
    st.stop()

# Helper function for validation
def validate_email(email):
    """Validate email format"""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))

def validate_url(url):
    """Validate URL format"""
    pattern = r"^(https?:\/\/)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$"
    return bool(re.match(pattern, url)) if url else True

def validate_phone(phone):
    """Validate phone number format"""
    pattern = r"^(\+\d{1,3}[-\s]?)?\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{4}$"
    return bool(re.match(pattern, phone)) if phone else True

# Helper function
def make_api_request(endpoint, method="GET", data=None, params=None):
    """Make API request with proper headers and authentication"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {st.session_state.access_token}"
    }
    
    url = f"{API_BASE_URL}/{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        if response.status_code in [200, 201, 204]:
            return response.json() if response.content else {"message": "Success"}
        else:
            error_msg = response.json() if response.content else {"detail": "Unknown error"}
            return {"error": f"Status {response.status_code}", "detail": error_msg}
    except Exception as e:
        return {"error": str(e)}

# Page title and description
st.title("Company Profile")
st.write("Complete your company profile to improve visibility and attract the right candidates.")

# Get current profile data
with st.spinner("Loading profile data..."):
    profile_data = make_api_request("profile")

if "error" in profile_data:
    st.error(f"Failed to load profile: {profile_data.get('error')}")
    st.stop()

# Create tabs for different sections of the profile
tabs = st.tabs(["Company Info", "Company Details", "Hiring Preferences", "Branding", "Settings"])

# Company Info Tab
with tabs[0]:
    with st.form("company_info_form"):
        st.subheader("Basic Company Information")
        
        # Company details from profile
        company_details = profile_data.get("company_details", {})
        
        # Required fields
        company_name = st.text_input(
            "Company Name*", 
            value=company_details.get("company_name", ""),
            help="Your company's legal name"
        )
        
        # Contact information
        st.subheader("Primary Contact")
        
        full_name = st.text_input(
            "Contact Person*", 
            value=profile_data.get("full_name", ""),
            help="Primary contact person for this account"
        )
        
        position = st.text_input(
            "Position/Title*", 
            value=profile_data.get("position", ""),
            help="Your position in the company"
        )
        
        email = st.text_input(
            "Email*", 
            value=profile_data.get("email", ""), 
            disabled=True,
            help="Your email is your unique identifier and cannot be changed"
        )
        
        phone = st.text_input(
            "Phone Number*",
            value=company_details.get("phone", ""),
            help="Format: +1-123-456-7890"
        )
        
        # Website and social media
        st.subheader("Online Presence")
        
        website = st.text_input(
            "Company Website*", 
            value=company_details.get("website", ""),
            help="Your company's official website (e.g., https://example.com)"
        )
        
        social_media = company_details.get("social_media", {})
        
        linkedin = st.text_input(
            "LinkedIn Company Page", 
            value=social_media.get("linkedin", ""),
            help="URL to your company's LinkedIn page"
        )
        
        twitter = st.text_input(
            "Twitter/X", 
            value=social_media.get("twitter", ""),
            help="URL to your company's Twitter/X profile"
        )
        
        facebook = st.text_input(
            "Facebook", 
            value=social_media.get("facebook", ""),
            help="URL to your company's Facebook page"
        )
        
        # Submit button
        company_info_submit = st.form_submit_button("Update Company Information")
    
    # Handle form submission
    if company_info_submit:
        # Validation
        validation_errors = []
        
        if not company_name:
            validation_errors.append("Company Name is required")
        
        if not full_name:
            validation_errors.append("Contact Person is required")
        
        if not position:
            validation_errors.append("Position/Title is required")
        
        if not phone:
            validation_errors.append("Phone Number is required")
        elif not validate_phone(phone):
            validation_errors.append("Phone Number format is invalid")
        
        if not website:
            validation_errors.append("Company Website is required")
        elif not validate_url(website):
            validation_errors.append("Website URL is not valid")
        
        if linkedin and not validate_url(linkedin):
            validation_errors.append("LinkedIn URL is not valid")
        
        if twitter and not validate_url(twitter):
            validation_errors.append("Twitter/X URL is not valid")
        
        if facebook and not validate_url(facebook):
            validation_errors.append("Facebook URL is not valid")
        
        if validation_errors:
            for error in validation_errors:
                st.error(error)
        else:
            # Build updated profile data
            updated_profile = {
                "full_name": full_name,
                "position": position,
                "company_details": {
                    "company_name": company_name,
                    "phone": phone,
                    "website": website,
                    "social_media": {
                        "linkedin": linkedin,
                        "twitter": twitter,
                        "facebook": facebook
                    }
                }
            }
            
            # Send update request
            with st.spinner("Updating company information..."):
                result = make_api_request("profile", method="PUT", data=updated_profile)
            
            if "error" in result:
                st.error(f"Failed to update company information: {result.get('error')}")
                if "detail" in result:
                    st.json(result.get("detail"))
            else:
                st.success("Company information updated successfully!")
                st.balloons()

# Company Details Tab
with tabs[1]:
    with st.form("company_details_form"):
        company_details = profile_data.get("company_details", {})
        
        st.subheader("Company Profile")
        
        # Industry and size
        industry = st.selectbox(
            "Industry*",
            options=[
                "Technology", "Finance", "Healthcare", "Education", "EdTech", "E-commerce", 
                "Manufacturing", "Retail", "Media", "Consulting", "Government",
                "Non-profit", "Energy", "Transportation", "Hospitality", "Real Estate",
                "Agriculture", "Entertainment", "Telecommunications", "Other"
            ],
            index=0 if not company_details.get("industry") else 
                  (lambda x: [
                    "Technology", "Finance", "Healthcare", "Education", "EdTech", "E-commerce", 
                    "Manufacturing", "Retail", "Media", "Consulting", "Government",
                    "Non-profit", "Energy", "Transportation", "Hospitality", "Real Estate",
                    "Agriculture", "Entertainment", "Telecommunications", "Other"
                  ].index(x) if x in [
                    "Technology", "Finance", "Healthcare", "Education", "EdTech", "E-commerce", 
                    "Manufacturing", "Retail", "Media", "Consulting", "Government",
                    "Non-profit", "Energy", "Transportation", "Hospitality", "Real Estate",
                    "Agriculture", "Entertainment", "Telecommunications", "Other"
                  ] else 0)(company_details.get("industry"))
        )
        
        company_size = st.selectbox(
            "Company Size*",
            options=["1-10 employees", "11-50 employees", "51-200 employees", "201-500 employees", "501+ employees"],
            index=0 if not company_details.get("company_size") else 
                  ["1-10 employees", "11-50 employees", "51-200 employees", "201-500 employees", "501+ employees"].index(company_details.get("company_size"))
        )
        
        # Convert founded_year to int if it's a string
        founded_year_value = company_details.get("founded_year", 2000)
        try:
            if isinstance(founded_year_value, str):
                founded_year_value = int(founded_year_value)
        except (ValueError, TypeError):
            founded_year_value = 2000
        
        founded_year = st.number_input(
            "Year Founded",
            min_value=1800,
            max_value=datetime.now().year,
            value=founded_year_value,
            help="When your company was established"
        )
        
        location = st.text_input(
            "Headquarters Location*", 
            value=company_details.get("location", ""),
            help="City, State, Country"
        )
        
        # Additional locations
        additional_locations = st.text_area(
            "Additional Office Locations",
            value=", ".join(company_details.get("additional_locations", [])),
            help="Separate with commas (e.g., New York, London, Tokyo)"
        )
        
        # Company description
        st.subheader("Company Description")
        
        description = st.text_area(
            "Company Description*", 
            value=company_details.get("description", ""),
            help="A detailed description of your company (100-1000 characters)",
            height=150
        )
        
        # Company culture
        st.subheader("Company Culture & Values")
        
        mission_statement = st.text_area(
            "Mission Statement", 
            value=company_details.get("mission_statement", ""),
            help="Your company's mission statement",
            height=100
        )
        
        values_input = st.text_area(
            "Company Values",
            value=", ".join(company_details.get("values", [])),
            help="Separate with commas (e.g., Innovation, Integrity, Teamwork)"
        )
        
        benefits_input = st.text_area(
            "Employee Benefits",
            value=", ".join(company_details.get("benefits", [])),
            help="Separate with commas (e.g., Health Insurance, Remote Work, Professional Development)"
        )
        
        company_details_submit = st.form_submit_button("Update Company Details")
    
    if company_details_submit:
        # Validation
        validation_errors = []
        
        if not industry:
            validation_errors.append("Industry is required")
        
        if not company_size:
            validation_errors.append("Company Size is required")
        
        if not location:
            validation_errors.append("Headquarters Location is required")
        
        if not description:
            validation_errors.append("Company Description is required")
        elif len(description) < 100:
            validation_errors.append("Company Description must be at least 100 characters")
        
        if validation_errors:
            for error in validation_errors:
                st.error(error)
        else:
            # Parse comma-separated text fields into lists
            values_list = [s.strip() for s in values_input.split(",") if s.strip()]
            benefits_list = [s.strip() for s in benefits_input.split(",") if s.strip()]
            additional_locations_list = [s.strip() for s in additional_locations.split(",") if s.strip()]
            
            # Build updated company details
            updated_company_details = {
                "company_details": {
                    "industry": industry,
                    "company_size": company_size,
                    "founded_year": founded_year,
                    "location": location,
                    "additional_locations": additional_locations_list,
                    "description": description,
                    "mission_statement": mission_statement,
                    "values": values_list,
                    "benefits": benefits_list
                }
            }
            
            # Send update request
            with st.spinner("Updating company details..."):
                result = make_api_request("profile", method="PUT", data=updated_company_details)
            
            if "error" in result:
                st.error(f"Failed to update company details: {result.get('error')}")
                if "detail" in result:
                    st.json(result.get("detail"))
            else:
                st.success("Company details updated successfully!")

# Hiring Preferences Tab
with tabs[2]:
    with st.form("hiring_preferences_form"):
        st.subheader("Hiring Needs")
        
        # Get existing preferences
        hiring_needs = profile_data.get("hiring_needs", [])
        preferred_skills = profile_data.get("preferred_skills", {})
        
        # Current hiring needs
        roles_input = st.text_area(
            "Current Open Positions*",
            value=", ".join(hiring_needs),
            help="Separate with commas (e.g., Software Engineer, Data Scientist, Product Manager)"
        )
        
        # Remote work policy
        remote_policy = st.selectbox(
            "Remote Work Policy",
            options=["Remote-first", "Hybrid", "In-office", "Flexible", "Varies by role"],
            index=0 if not profile_data.get("remote_policy") else 
                 ["Remote-first", "Hybrid", "In-office", "Flexible", "Varies by role"].index(profile_data.get("remote_policy"))
        )
        
        # Hiring timeline
        hiring_timeline = st.selectbox(
            "Hiring Timeline",
            options=["Immediate", "Within 1 month", "1-3 months", "3+ months", "Ongoing"],
            index=0 if not profile_data.get("hiring_timeline") else 
                 ["Immediate", "Within 1 month", "1-3 months", "3+ months", "Ongoing"].index(profile_data.get("hiring_timeline"))
        )
        
        # Skills preferences
        st.subheader("Preferred Skills")
        
        st.write("Technical Skills")
        technical_skills_input = st.text_area(
            "Technical Skills*",
            value=", ".join(preferred_skills.get("technical", [])),
            help="Separate with commas (e.g., Python, React, AWS, Machine Learning)"
        )
        
        st.write("Soft Skills")
        soft_skills_input = st.text_area(
            "Soft Skills",
            value=", ".join(preferred_skills.get("soft", [])),
            help="Separate with commas (e.g., Communication, Leadership, Problem-solving)"
        )
        
        # Experience preferences
        st.subheader("Experience Preferences")
        
        min_experience = st.number_input(
            "Minimum Years of Experience",
            min_value=0,
            max_value=20,
            value=profile_data.get("min_experience", 0),
            help="Minimum years of experience for most positions"
        )
        
        education_level = st.multiselect(
            "Preferred Education Levels",
            options=["High School", "Associate's Degree", "Bachelor's Degree", "Master's Degree", "PhD", "No preference"],
            default=profile_data.get("education_level", ["No preference"]),
            help="Select all that apply for your typical positions"
        )
        
        # Recommendation Engine Settings
        st.subheader("Candidate Recommendation Settings")
        
        rec_prefs = profile_data.get("recommendation_preferences", {})
        
        st.write("Adjust weights to prioritize different factors in candidate recommendations")
        
        col1, col2 = st.columns(2)
        with col1:
            skills_weight = st.slider(
                "Skills Match Weight",
                min_value=0.0,
                max_value=1.0,
                value=rec_prefs.get("skills_weight", 0.7),
                step=0.1,
                help="How important matching skills are in recommendations"
            )
            
            experience_weight = st.slider(
                "Experience Weight",
                min_value=0.0,
                max_value=1.0,
                value=rec_prefs.get("experience_weight", 0.5),
                step=0.1,
                help="How important years of experience are in recommendations"
            )
        
        with col2:
            education_weight = st.slider(
                "Education Weight",
                min_value=0.0,
                max_value=1.0,
                value=rec_prefs.get("education_weight", 0.3),
                step=0.1,
                help="How important education level is in recommendations"
            )
            
            location_weight = st.slider(
                "Location Weight",
                min_value=0.0,
                max_value=1.0,
                value=rec_prefs.get("location_weight", 0.2),
                step=0.1,
                help="How important candidate location is in recommendations"
            )
        
        # Submit button
        hiring_submit = st.form_submit_button("Update Hiring Preferences")
    
    if hiring_submit:
        # Validation
        validation_errors = []
        
        if not roles_input.strip():
            validation_errors.append("At least one open position is required")
        
        if not technical_skills_input.strip():
            validation_errors.append("At least one technical skill is required")
        
        if validation_errors:
            for error in validation_errors:
                st.error(error)
        else:
            # Parse comma-separated text fields into lists
            roles_list = [s.strip() for s in roles_input.split(",") if s.strip()]
            technical_skills_list = [s.strip() for s in technical_skills_input.split(",") if s.strip()]
            soft_skills_list = [s.strip() for s in soft_skills_input.split(",") if s.strip()]
            
            # Build updated preferences data
            updated_preferences = {
                "hiring_needs": roles_list,
                "remote_policy": remote_policy,
                "hiring_timeline": hiring_timeline,
                "min_experience": min_experience,
                "education_level": education_level,
                "preferred_skills": {
                    "technical": technical_skills_list,
                    "soft": soft_skills_list
                },
                "recommendation_preferences": {
                    "skills_weight": skills_weight,
                    "experience_weight": experience_weight,
                    "education_weight": education_weight,
                    "location_weight": location_weight
                }
            }
            
            # Send update request
            with st.spinner("Updating hiring preferences..."):
                result = make_api_request("profile", method="PUT", data=updated_preferences)
            
            if "error" in result:
                st.error(f"Failed to update hiring preferences: {result.get('error')}")
                if "detail" in result:
                    st.json(result.get("detail"))
            else:
                st.success("Hiring preferences updated successfully!")

# Display notification about recommendation impacts
st.info("""
💡 **Tip:** Keeping your company profile up-to-date with accurate details and hiring preferences 
helps the recommendation system find better candidate matches for your roles!
""")

# Company analytics section
st.subheader("Company Profile Analytics")
with st.expander("View Profile Performance"):
    # This would typically be fetched from an analytics API endpoint
    st.write("Profile visibility and engagement metrics:")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Profile Views", "487", "+12%")
    with col2:
        st.metric("Candidate Applications", "64", "+8%")
    with col3:
        st.metric("Search Appearances", "1,243", "+21%")
    
    st.write("Complete your company profile to improve visibility to candidates.")
    progress = 85  # This would be calculated based on profile completeness
    st.progress(progress / 100)
    st.write(f"Profile Completeness: {progress}%")

# Branding Tab
with tabs[3]:
    st.subheader("Company Branding")
    
    # Company logo
    st.write("**Company Logo**")
    logo_col1, logo_col2 = st.columns([1, 2])
    
    with logo_col1:
        # This would typically display the existing logo
        st.image("https://via.placeholder.com/150x150.png?text=Logo", width=150)
    
    with logo_col2:
        with st.form("logo_upload_form"):
            logo_upload = st.file_uploader(
                "Upload company logo", 
                type=["jpg", "png", "jpeg"],
                help="Recommended size: 400x400 pixels, max 2MB"
            )
            logo_submit = st.form_submit_button("Upload Logo")
        
        if logo_submit:
            if logo_upload is not None:
                # This would typically upload to an API endpoint
                with st.spinner("Uploading logo..."):
                    # Simulate API call for logo upload
                    st.success("Logo uploaded successfully!")
            else:
                st.error("Please select a file to upload")
    
    # Company photos
    st.write("**Company Photos**")
    
    with st.form("photos_upload_form"):
        st.write("Upload photos of your workplace, team, or company events")
        
        photos_upload = st.file_uploader(
            "Upload company photos", 
            type=["jpg", "png", "jpeg"],
            accept_multiple_files=True,
            help="Max 5 photos, 5MB each"
        )
        
        photos_submit = st.form_submit_button("Upload Photos")
    
    if photos_submit:
        if photos_upload:
            # This would typically upload to an API endpoint
            with st.spinner("Uploading photos..."):
                # Simulate API call for photos upload
                st.success(f"{len(photos_upload)} photos uploaded successfully!")
        else:
            st.error("Please select photos to upload")
    
    # Company video
    st.write("**Company Video**")
    
    with st.form("video_form"):
        video_url = st.text_input(
            "YouTube or Vimeo URL",
            value=profile_data.get("company_details", {}).get("video_url", ""),
            help="Enter a YouTube or Vimeo URL to showcase your company"
        )
        
        video_submit = st.form_submit_button("Save Video URL")
    
    if video_submit:
        if video_url:
            if validate_url(video_url):
                # Handle video URL update
                with st.spinner("Saving video URL..."):
                    result = make_api_request("profile", method="PUT", data={
                        "company_details": {"video_url": video_url}
                    })
                
                if "error" in result:
                    st.error(f"Failed to save video URL: {result.get('error')}")
                else:
                    st.success("Video URL saved successfully!")
            else:
                st.error("Please enter a valid URL")
    
    # Employer branding statement
    st.write("**Employer Branding Statement**")
    
    with st.form("branding_statement_form"):
        branding_statement = st.text_area(
            "Why Work With Us",
            value=profile_data.get("company_details", {}).get("branding_statement", ""),
            help="Tell candidates why they should work at your company (max 500 characters)",
            height=150
        )
        
        branding_submit = st.form_submit_button("Save Branding Statement")
    
    if branding_submit:
        if branding_statement:
            if len(branding_statement) > 500:
                st.error("Branding statement must be 500 characters or less")
            else:
                # Handle branding statement update
                with st.spinner("Saving branding statement..."):
                    result = make_api_request("profile", method="PUT", data={
                        "company_details": {"branding_statement": branding_statement}
                    })
                
                if "error" in result:
                    st.error(f"Failed to save branding statement: {result.get('error')}")
                else:
                    st.success("Branding statement saved successfully!")

# Settings Tab
with tabs[4]:
    st.subheader("Account Settings")
    
    # Notification settings
    with st.form("notification_settings_form"):
        st.subheader("Notification Settings")
        
        # Email notification settings
        email_notifications = profile_data.get("email_notifications", {})
        
        st.write("**Email Notifications**")
        
        new_applicants = st.checkbox(
            "New Job Applicants",
            value=email_notifications.get("new_applicants", True),
            help="Receive email notifications when candidates apply to your jobs"
        )
        
        candidate_recommendations = st.checkbox(
            "Candidate Recommendations",
            value=email_notifications.get("candidate_recommendations", True),
            help="Receive weekly candidate recommendations for your open positions"
        )
        
        account_updates = st.checkbox(
            "Account Updates",
            value=email_notifications.get("account_updates", True),
            help="Receive updates about your account and new features"
        )
        
        # Notification frequency
        notification_frequency = st.selectbox(
            "Email Frequency",
            options=["Real-time", "Daily Digest", "Weekly Digest", "Never"],
            index=0 if not email_notifications.get("frequency") else 
                 ["Real-time", "Daily Digest", "Weekly Digest", "Never"].index(email_notifications.get("frequency"))
        )
        
        notification_submit = st.form_submit_button("Save Notification Settings")
    
    if notification_submit:
        # Build updated notification settings
        updated_notifications = {
            "email_notifications": {
                "new_applicants": new_applicants,
                "candidate_recommendations": candidate_recommendations,
                "account_updates": account_updates,
                "frequency": notification_frequency
            }
        }
        
        # Send update request
        with st.spinner("Updating notification settings..."):
            result = make_api_request("profile/settings", method="PUT", data=updated_notifications)
        
        if "error" in result:
            st.error(f"Failed to update notification settings: {result.get('error')}")
        else:
            st.success("Notification settings updated successfully!")
    
    # Privacy settings
    with st.form("privacy_settings_form"):
        st.subheader("Privacy Settings")
        
        privacy_settings = profile_data.get("privacy_settings", {})
        
        profile_visibility = st.selectbox(
            "Company Profile Visibility",
            options=["Public", "Registered Users Only", "Private"],
            index=0 if not privacy_settings.get("profile_visibility") else 
                 ["Public", "Registered Users Only", "Private"].index(privacy_settings.get("profile_visibility"))
        )
        
        show_company_stats = st.checkbox(
            "Show Company Statistics",
            value=privacy_settings.get("show_company_stats", True),
            help="Show company statistics like number of employees, growth rate, etc."
        )
        
        allow_candidate_messages = st.checkbox(
            "Allow Direct Messages from Candidates",
            value=privacy_settings.get("allow_candidate_messages", True),
            help="Allow candidates to message you directly through the platform"
        )
        
        privacy_submit = st.form_submit_button("Save Privacy Settings")
    
    if privacy_submit:
        # Build updated privacy settings
        updated_privacy = {
            "privacy_settings": {
                "profile_visibility": profile_visibility,
                "show_company_stats": show_company_stats,
                "allow_candidate_messages": allow_candidate_messages
            }
        }
        
        # Send update request
        with st.spinner("Updating privacy settings..."):
            result = make_api_request("profile/privacy", method="PUT", data=updated_privacy)
        
        if "error" in result:
            st.error(f"Failed to update privacy settings: {result.get('error')}")
        else:
            st.success("Privacy settings updated successfully!")
    
    # Change password
    with st.form("change_password_form"):
        st.subheader("Change Password")
        
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        password_submit = st.form_submit_button("Change Password")
    
    if password_submit:
        # Validation
        validation_errors = []
        
        if not current_password:
            validation_errors.append("Current password is required")
        
        if not new_password:
            validation_errors.append("New password is required")
        elif len(new_password) < 8:
            validation_errors.append("New password must be at least 8 characters")
        
        if new_password != confirm_password:
            validation_errors.append("New password and confirmation do not match")
        
        if validation_errors:
            for error in validation_errors:
                st.error(error)
        else:
            # Send password change request
            password_data = {
                "current_password": current_password,
                "new_password": new_password
            }
            
            with st.spinner("Changing password..."):
                result = make_api_request("auth/change-password", method="POST", data=password_data)
            
            if "error" in result:
                st.error(f"Failed to change password: {result.get('error')}")
            else:
                st.success("Password changed successfully!")
    
    # Danger zone
    st.subheader("Danger Zone")
    
    with st.expander("Delete Account"):
        st.warning("""
        **Warning:** Deleting your account is permanent and cannot be undone.
        All your data, including company profile, job postings, and candidate applications will be permanently deleted.
        """)
        
        confirm_delete = st.text_input(
            "Type 'DELETE' to confirm account deletion",
            help="This action is permanent and cannot be undone"
        )
        
        if st.button("Delete Account", type="primary"):
            if confirm_delete != "DELETE":
                st.error("Please type 'DELETE' to confirm account deletion")
            else:
                # Send delete request
                with st.spinner("Deleting account..."):
                    result = make_api_request("profile", method="DELETE")
                
                if "error" in result:
                    st.error(f"Failed to delete account: {result.get('error')}")
                else:
                    # Clear session state
                    for key in ["authenticated", "user_type", "access_token"]:
                        if key in st.session_state:
                            del st.session_state[key]
                    
                    st.success("Account deleted successfully.")
                    st.info("You will be redirected to the login page in a few seconds...")
                    st.experimental_rerun()

# Add help box at the bottom
st.info("""
💡 **Tip:** Complete your company profile to improve visibility to potential candidates.
The more information you provide, the better we can match you with suitable candidates for your roles.
""") 