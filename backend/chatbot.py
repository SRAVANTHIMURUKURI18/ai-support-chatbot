import os
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Student, Ticket

user_states = {}

def process_chat_message(message: str, session_id: str) -> str:
    db: Session = SessionLocal()
    try:
        clean_email = session_id.lower().strip().replace("[user email:", "").replace("]", "").strip()
        msg_lower = message.lower().strip()
        
        current_state = user_states.get(clean_email, "main_menu")

        # 1. Global Navigation & Quick Reply Interceptors (Handles all button clicks instantly)
        if "menu" in msg_lower or msg_lower == "hi" or msg_lower == "hello" or msg_lower == "start":
            user_states[clean_email] = "main_menu"
            return (
                "Welcome to Vishnu Institute of Technology IT Helpdesk! Please select an option below:\n\n"
                "1️⃣ **Create a Support Ticket**\n"
                "2️⃣ **Retrieve College Info**\n"
                "3️⃣ **Display Active Tickets**\n"
                "4️⃣ **Reset Portal Password**\n"
                "5️⃣ **Explore Campus Clubs & Join**"
            )

        # Catch explicit EAPCET Info button clicks from anywhere
        if "eapcet info" in msg_lower or "eamcet info" in msg_lower:
            user_states[clean_email] = "main_menu"
            return (
                "🎓 **VISHNU INSTITUTE OF TECHNOLOGY :: BHIMAVARAM**\n"
                "📊 **EAPCET - 2025 (1st Phase) Last Ranks Admitted:**\n\n"
                
                "**CSE**\n"
                "[OC] MALE : 4433 || FEMALE : 5213\n"
                "[EWS] MALE : 5032 || FEMALE : 5744\n"
                "[BC_A] MALE : 8905 || FEMALE : 12366\n"
                "[BC_B] MALE : 7269 || FEMALE : 10315\n"
                "[BC_C] MALE : -- || FEMALE : 28955\n"
                "[BC_D] MALE : 5976 || FEMALE : 6601\n"
                "[BC_E] MALE : 21625 || FEMALE : 14687\n"
                "[SC] MALE : 128632 || FEMALE : 30515\n"
                "[ST] MALE : 74436 || FEMALE : 79778\n\n"

                "**IT**\n"
                "[OC] MALE : 13178 || FEMALE : 12907\n"
                "[EWS] MALE : 14633 || FEMALE : 14652\n"
                "[BC_A] MALE : 26915 || FEMALE : 29842\n"
                "[BC_B] MALE : 20611 || FEMALE : 20938\n"
                "[BC_C] MALE : 47210 || FEMALE : --\n"
                "[BC_D] MALE : 20065 || FEMALE : 19761\n"
                "[BC_E] MALE : 37859 || FEMALE : 33808\n"
                "[SC] MALE : 116010 || FEMALE : 127581\n"
                "[ST] MALE : 155318 || FEMALE : 146405\n\n"

                "**AI & DS**\n"
                "[OC] MALE : 6625 || FEMALE : 7399\n"
                "[EWS] MALE : 7191 || FEMALE : 7688\n"
                "[BC_A] MALE : 12672 || FEMALE : 19598\n"
                "[BC_B] MALE : 12281 || FEMALE : 12442\n"
                "[BC_C] MALE : 78325 || FEMALE : --\n"
                "[BC_D] MALE : 8925 || FEMALE : 10790\n"
                "[BC_E] MALE : 18699 || FEMALE : 26815\n"
                "[SC] MALE : 37990 || FEMALE : 64207\n"
                "[ST] MALE : 102357 || FEMALE : 113609\n\n"

                "**AI & ML**\n"
                "[OC] MALE : 4811 || FEMALE : 6105\n"
                "[EWS] MALE : 5377 || FEMALE : 6346\n"
                "[BC_A] MALE : 10725 || FEMALE : 11919\n"
                "[BC_B] MALE : 8565 || FEMALE : 9478\n"
                "[BC_C] MALE : -- || FEMALE : --\n"
                "[BC_D] MALE : 6907 || FEMALE : 8534\n"
                "[BC_E] MALE : 11199 || FEMALE : 28862\n"
                "[SC] MALE : 162962 || FEMALE : 33487\n"
                "[ST] MALE : 80396 || FEMALE : 90802\n\n"

                "**ECE**\n"
                "[OC] MALE : 8364 || FEMALE : 12064\n"
                "[EWS] MALE : 11746 || FEMALE : 12604\n"
                "[BC_A] MALE : 16549 || FEMALE : 24481\n"
                "[BC_B] MALE : 16418 || FEMALE : 17163\n"
                "[BC_C] MALE : 22974 || FEMALE : --\n"
                "[BC_D] MALE : 10762 || FEMALE : 15290\n"
                "[BC_E] MALE : 43923 || FEMALE : 50516\n"
                "[SC] MALE : 46800 || FEMALE : 65593\n"
                "[ST] MALE : 93073 || FEMALE : 105938\n\n"

                "📋 **Required Admission Documents:**\n"
                "1. EAMCET/EAPCET Rank Card & Hall Ticket\n"
                "2. Study Certificates (6th to 10+2)\n"
                "3. Transfer Certificate (TC)\n"
                "4. Income & Caste Certificates\n\n"
                "📍 **Admission Venue:** Ground floor of the main administrative block.\n\n"
                "Type **'menu'** to return to main options."
            )

        if "college info" in msg_lower:
            user_states[clean_email] = "rag_submenu"
            return (
                "📚 **College Information Submenu**\n"
                "Select a topic below:\n\n"
                "• 1. Campus Facilities & Food\n"
                "• 2. College Websites & Portals\n"
                "• 3. Placement Stats (2021-2026)\n"
                "• 4. Faculty & Permissions (HOD/TPO)\n"
                "• 5. EAPCET 2025 Cutoffs & Admissions\n"
                "• 6. Hostel Outing Application Guide\n\n"
                "Type the topic name or number."
            )

        if "create ticket" in msg_lower or msg_lower == "1":
            user_states[clean_email] = "creating_ticket_category"
            return (
                "🎫 **Create Support Ticket**\n"
                "Please select the category of your issue:\n\n"
                "1. Academic / Attendance\n"
                "2. Hostel / Mess\n"
                "3. Portal / IT Infrastructure\n"
                "4. Fee / Accounts\n\n"
                "Type the category name or number."
            )

        if "my tickets" in msg_lower or msg_lower == "3" or "display active tickets" in msg_lower:
            user_states[clean_email] = "main_menu"
            student = db.query(Student).filter(Student.email == clean_email).first()
            if not student:
                return f"⚠️ Student profile not found for `{clean_email}`. Please re-login.\n\nType **'menu'** to return."
            
            tickets = db.query(Ticket).filter(Ticket.student_id == student.id).all()
            if not tickets:
                return "📋 You have **0 active tickets** currently registered.\n\nType **'menu'** to return to main options."
            
            response_str = "📋 **Your Support Tickets:**\n\n"
            for t in tickets:
                response_str += f"• **Ticket #{t.id}** [{t.status}] - {t.category}: {t.description}\n"
            response_str += "\nType **'menu'** to return to main options."
            return response_str

        # 2. State Machine Routing
        if current_state == "main_menu":
            if "password" in msg_lower or "reset" in msg_lower or msg_lower == "4":
                return (
                    "🔐 **Portal Password Reset**\n"
                    "You can easily update your password using the profile page settings (click the profile icon at the top right).\n\n"
                    "Type **'menu'** to return to main options."
                )

            elif "club" in msg_lower or "join" in msg_lower or msg_lower == "5":
                return (
                    "🌟 **Campus Clubs & Activities:**\n"
                    "Vishnu Institute of Technology features vibrant technical and cultural chapters including:\n"
                    "• Coding Clubs (ACM, CSI, IEEE)\n"
                    "• Cultural & Dance Clubs\n"
                    "• NSS & Robotics Society\n\n"
                    "Visit the Student Affairs office to join!\n\n"
                    "Type **'menu'** to return to main options."
                )
            
            else:
                return "I didn't quite catch that. Please type **'menu'** to see the main options."

        elif current_state == "rag_submenu":
            user_states[clean_email] = "main_menu"
            
            if "library" in msg_lower or "1" in msg_lower:
                return "📖 **Central Library Timings:**\nOpen from **8:00 AM to 8:00 PM** on working days and **9:00 AM to 1:00 PM** on Saturdays.\n\nType **'menu'** to return to main options."
            elif "fee" in msg_lower or "2" in msg_lower:
                return "💳 **Fee Counter Details:**\nLocated in the main administrative block. Open from **9:30 AM to 4:00 PM** on working days.\n\nType **'menu'** to return to main options."
            elif "biometric" in msg_lower or "3" in msg_lower:
                return "⏰ **Biometric Timings:**\nMandatory logging between **8:30 AM to 9:00 AM** and evening departure at **4:10 PM**.\n\nType **'menu'** to return to main options."
            elif "event" in msg_lower or "fiesta" in msg_lower or "4" in msg_lower:
                return "🎉 **Vishnu Fiesta Event Timings:**\nAnnual technical and cultural fest scheduled for the last week of March at the open-air auditorium.\n\nType **'menu'** to return to main options."
            elif "eamcet" in msg_lower or "eapcet" in msg_lower or "cutoff" in msg_lower or "doc" in msg_lower or "venue" in msg_lower or "5" in msg_lower:
                return (
                    "🎓 **VISHNU INSTITUTE OF TECHNOLOGY :: BHIMAVARAM**\n"
                    "📊 **EAPCET - 2025 (1st Phase) Last Ranks Admitted:**\n\n"
                    
                    "**CSE**\n"
                    "[OC] MALE : 4433 || FEMALE : 5213\n"
                    "[EWS] MALE : 5032 || FEMALE : 5744\n"
                    "[BC_A] MALE : 8905 || FEMALE : 12366\n"
                    "[BC_B] MALE : 7269 || FEMALE : 10315\n"
                    "[BC_C] MALE : -- || FEMALE : 28955\n"
                    "[BC_D] MALE : 5976 || FEMALE : 6601\n"
                    "[BC_E] MALE : 21625 || FEMALE : 14687\n"
                    "[SC] MALE : 128632 || FEMALE : 30515\n"
                    "[ST] MALE : 74436 || FEMALE : 79778\n\n"

                    "**IT**\n"
                    "[OC] MALE : 13178 || FEMALE : 12907\n"
                    "[EWS] MALE : 14633 || FEMALE : 14652\n"
                    "[BC_A] MALE : 26915 || FEMALE : 29842\n"
                    "[BC_B] MALE : 20611 || FEMALE : 20938\n"
                    "[BC_C] MALE : 47210 || FEMALE : --\n"
                    "[BC_D] MALE : 20065 || FEMALE : 19761\n"
                    "[BC_E] MALE : 37859 || FEMALE : 33808\n"
                    "[SC] MALE : 116010 || FEMALE : 127581\n"
                    "[ST] MALE : 155318 || FEMALE : 146405\n\n"

                    "**AI & DS**\n"
                    "[OC] MALE : 6625 || FEMALE : 7399\n"
                    "[EWS] MALE : 7191 || FEMALE : 7688\n"
                    "[BC_A] MALE : 12672 || FEMALE : 19598\n"
                    "[BC_B] MALE : 12281 || FEMALE : 12442\n"
                    "[BC_C] MALE : 78325 || FEMALE : --\n"
                    "[BC_D] MALE : 8925 || FEMALE : 10790\n"
                    "[BC_E] MALE : 18699 || FEMALE : 26815\n"
                    "[SC] MALE : 37990 || FEMALE : 64207\n"
                    "[ST] MALE : 102357 || FEMALE : 113609\n\n"

                    "**AI & ML**\n"
                    "[OC] MALE : 4811 || FEMALE : 6105\n"
                    "[EWS] MALE : 5377 || FEMALE : 6346\n"
                    "[BC_A] MALE : 10725 || FEMALE : 11919\n"
                    "[BC_B] MALE : 8565 || FEMALE : 9478\n"
                    "[BC_C] MALE : -- || FEMALE : --\n"
                    "[BC_D] MALE : 6907 || FEMALE : 8534\n"
                    "[BC_E] MALE : 11199 || FEMALE : 28862\n"
                    "[SC] MALE : 162962 || FEMALE : 33487\n"
                    "[ST] MALE : 80396 || FEMALE : 90802\n\n"

                    "**ECE**\n"
                    "[OC] MALE : 8364 || FEMALE : 12064\n"
                    "[EWS] MALE : 11746 || FEMALE : 12604\n"
                    "[BC_A] MALE : 16549 || FEMALE : 24481\n"
                    "[BC_B] MALE : 16418 || FEMALE : 17163\n"
                    "[BC_C] MALE : 22974 || FEMALE : --\n"
                    "[BC_D] MALE : 10762 || FEMALE : 15290\n"
                    "[BC_E] MALE : 43923 || FEMALE : 50516\n"
                    "[SC] MALE : 46800 || FEMALE : 65593\n"
                    "[ST] MALE : 93073 || FEMALE : 105938\n\n"

                    "📋 **Required Admission Documents:**\n"
                    "1. EAMCET/EAPCET Rank Card & Hall Ticket\n"
                    "2. Study Certificates (6th to 10+2)\n"
                    "3. Transfer Certificate (TC)\n"
                    "4. Income & Caste Certificates\n\n"
                    "📍 **Admission Venue:** Ground floor of the main administrative block.\n\n"
                    "Type **'menu'** to return to main options."
                )
            else:
                return "ℹ️ **Hostel Outing Application Guide:**\nSubmit requests via the student portal 24 hours prior. Parent approval is mandatory.\n\nType **'menu'** to return."

        elif current_state == "creating_ticket_category":
            user_states[clean_email] = "creating_ticket_desc"
            cat_map = {"1": "Academic / Attendance", "2": "Hostel / Mess", "3": "Portal / IT Infrastructure", "4": "Fee / Accounts"}
            selected_cat = cat_map.get(msg_lower, message)
            user_states[clean_email + "_category"] = selected_cat
            return f"📝 Category selected: **{selected_cat}**.\nPlease provide a brief description of your issue:"

        elif current_state == "creating_ticket_desc":
            category = user_states.pop(clean_email + "_category", "General")
            user_states[clean_email] = "main_menu"

            student = db.query(Student).filter(Student.email == clean_email).first()
            if student:
                new_ticket = Ticket(
                    student_id=student.id,
                    category=category,
                    description=message,
                    status="Active"
                )
                db.add(new_ticket)
                db.commit()
                return f"✅ **Support Ticket Created Successfully!**\n\n• **Category:** {category}\n• **Description:** {message}\n• **Status:** Active\n\nType **'menu'** to return to main options."
            else:
                return f"⚠️ Error identifying student profile for `{clean_email}`. Please re-login.\n\nType **'menu'** to return."

        user_states[clean_email] = "main_menu"
        return "Type **'menu'** to view main options."

    except Exception as e:
        return f"An error occurred: {str(e)}\n\nType **'menu'** to restart."
    finally:
        db.close()