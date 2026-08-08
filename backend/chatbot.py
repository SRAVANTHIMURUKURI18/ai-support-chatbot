import json
import os
import re
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models import Student, Ticket
from backend.rag_engine import query_rag

user_states = {}

# Load JSON FAQ dataset for static info
FAQ_PATH = os.path.join(os.path.dirname(__file__), "faq_dataset.json")
if os.path.exists(FAQ_PATH):
    with open(FAQ_PATH, "r") as f:
        FAQ_DATA = json.load(f)
else:
    FAQ_DATA = {}

# Ensure detailed EAMCET breakdown is always available
if "eapcet" not in FAQ_DATA:
    FAQ_DATA["eapcet"] = [{
        "question": "AP-EAMCET Cutoffs & Admissions",
        "answer": (
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
            "📍 **Admission Venue:** Ground floor of the main administrative block."
        )
    }]

def process_chat_message(message: str, session_id: str) -> str:
    db: Session = SessionLocal()
    try:
        clean_email = session_id.lower().strip().replace("[user email:", "").replace("]", "").strip()
        msg_lower = message.lower().strip()
        
        current_state = user_states.get(clean_email, "main_menu")
        student = db.query(Student).filter(Student.email == clean_email).first()

        # Handle gratitude / thank you inputs politely
        if any(word in msg_lower for word in ["thank", "thanks", "thank you", "thx"]):
            user_states[clean_email] = "main_menu"
            return "You're very welcome! Let me know if you need help with anything else. Type **'menu'** anytime to see the main options."

        # Handle confirmation / casual acknowledgements
        if msg_lower in ["ok", "okay", "k", "bye", "goodbye"]:
            user_states[clean_email] = "main_menu"
            if msg_lower in ["bye", "goodbye"]:
                return "Goodbye! Have a great day ahead. Type **'menu'** whenever you need assistance again."
            return "Got it! Type **'menu'** whenever you want to return to the main options."

        # 0. Handle Page Load Initialization Flag & Casual User Greetings cleanly without menu dump
        if msg_lower == "__init_greeting__" or any(w in msg_lower for w in ["hi", "hello", "hey", "start", "greetings", "good morning", "good afternoon", "good evening", "morning", "evening"]):
            user_states[clean_email] = "main_menu"
            name_to_display = student.name if student else "Student"
            return (
                f"Hello {name_to_display}! 👋 Welcome to the Vishnu Institute of Technology IT Helpdesk.\n\n"
                "How can I assist you today? You can ask me any question directly, or type **'menu'** if you want to view the main options."
            )

        # 🚨 PRIORITY 1: TICKET CLOSING / RESOLUTION REQUEST
        if any(term in msg_lower for term in ["close ticket", "resolve ticket", "ticket #", "mark resolved"]):
            user_states[clean_email] = "main_menu"
            if not student:
                return f"⚠️ Student profile not found for `{clean_email}`. Please re-login.\n\nType **'menu'** to return."
            
            ticket_nums = re.findall(r'\d+', message)
            if ticket_nums:
                target_id = int(ticket_nums[0])
                ticket_obj = db.query(Ticket).filter(Ticket.id == target_id, Ticket.student_id == student.id).first()
                if ticket_obj:
                    ticket_obj.status = "Resolved"
                    db.commit()
                    return f"✅ **Ticket #{target_id} has been marked as Resolved successfully!**\n\nType **'menu'** to return to main options."
                else:
                    return f"❌ **Error:** Could not find an active ticket with ID #{target_id} under your profile.\n\nType **'menu'** to return."
            else:
                return "⚠️ Please specify the ticket number you wish to close (e.g., *'close ticket #12'*).\n\nType **'menu'** to return."

        # 🚨 PRIORITY 2: AUTOMATED TICKET INTERCEPTOR FOR ACTUAL SYSTEM/INFRASTRUCTURE FAILURES
        is_informational_query = any(phrase in msg_lower for phrase in ["can i", "how", "what are", "rules", "request", "is there", "check", "timings", "timing", "where"])
        
        issue_keywords = ["wifi", "internet", "network", "router", "connection", "transaction failed", "payment failed", "portal crashed", "bug", "error in portal"]
        if any(kw in msg_lower for kw in issue_keywords) and not is_informational_query and current_state == "main_menu":
            category = "IT Support"
            if any(term in msg_lower for term in ["result", "marks", "exam", "grade"]):
                category = "Academic"
            elif any(term in msg_lower for term in ["hostel", "room", "mess"]):
                category = "Hostel"
            elif any(term in msg_lower for term in ["fee", "payment", "transaction"]):
                category = "Fee"

            user_states[clean_email] = "main_menu"
            if student:
                new_ticket = Ticket(
                    student_id=student.id,
                    category=category,
                    description=message,
                    status="Open"
                )
                db.add(new_ticket)
                db.commit()
                return (
                    f"✅ **Support Ticket Created & Saved to Database Automatically!**\n\n"
                    f"• **Category:** {category}\n"
                    f"• **Description:** {message}\n"
                    f"• **Status:** Open\n\n"
                    "Type **'menu'** to return to main options."
                )

        # 1. Handle Active Submenu States FIRST
        if current_state == "rag_submenu":
            user_states[clean_email] = "main_menu"
            
            mapping = {
                "1": "academics", "academic": "academics",
                "2": "hostel", "hostel": "hostel",
                "mess": "mess", "3": "placements", "placement": "placements",
                "4": "library", "library": "library",
                "5": "examination", "exam": "examination",
                "6": "fee", "fee": "fee",
                "7": "it_support", "it": "it_support",
                "8": "eapcet", "eamcet": "eapcet", "admission": "eapcet"
            }
            
            key = mapping.get(msg_lower, "academics")
            category_data = FAQ_DATA.get(key, [])
            
            if key == "eapcet":
                ans = category_data[0]["answer"] if category_data else ""
                return f"{ans}\n\nType **'menu'** to return to main options."

            res_str = f"📖 **Quick Overview regarding {key.upper()}:**\n\n"
            for item in category_data[:3]:
                res_str += f"• **{item['question']}**\n  {item['answer']}\n\n"
            res_str += "Type **'menu'** to return to main options or ask a specific question!"
            return res_str

        elif current_state == "creating_ticket_category":
            user_states[clean_email] = "creating_ticket_desc"
            cat_map = {
                "1": "Academic", "2": "Hostel", "3": "Library", "4": "Placement",
                "5": "Fee", "6": "IT Support", "7": "Examination", "8": "Administration"
            }
            selected_cat = cat_map.get(msg_lower, message.title())
            user_states[clean_email + "_category"] = selected_cat
            return f"📝 Category selected: **{selected_cat}**.\nPlease provide a comprehensive description of your issue:"

        elif current_state == "creating_ticket_desc":
            category = user_states.pop(clean_email + "_category", "General")
            user_states[clean_email] = "main_menu"

            if student:
                new_ticket = Ticket(
                    student_id=student.id,
                    category=category,
                    description=message,
                    status="Open"
                )
                db.add(new_ticket)
                db.commit()
                return f"✅ **Support Ticket Created & Saved to Database!**\n\n• **Category:** {category}\n• **Description:** {message}\n• **Status:** Open\n\nType **'menu'** to return to main options."
            else:
                return f"⚠️ Error identifying student profile for `{clean_email}`. Please re-login.\n\nType **'menu'** to return."

        elif current_state == "reset_pwd_old":
            user_states[clean_email + "_old_pwd"] = message
            user_states[clean_email] = "reset_pwd_new"
            return "🔐 Please enter your **new password**:"

        elif current_state == "reset_pwd_new":
            old_pwd = user_states.pop(clean_email + "_old_pwd", "")
            new_pwd = message
            user_states[clean_email] = "main_menu"

            if not student:
                return f"⚠️ Student profile not found for `{clean_email}`.\n\nType **'menu'** to return."
            
            if student.password != old_pwd:
                return "❌ **Password Reset Failed:** Your current password is incorrect.\n\nType **'menu'** to return."

            student.password = new_pwd
            db.commit()
            return "✅ **Password Updated Successfully!** Your portal password has been changed in the database.\n\nType **'menu'** to return to main options."

        elif current_state == "club_interest":
            user_states[clean_email] = "main_menu"
            if "yes" in msg_lower or "y" in msg_lower:
                return (
                    "🎉 **Great! Here are the official contact details and coordinators for all campus clubs:**\n\n"
                    "• **E-Cell (Entrepreneurship Cell):** Coordinator - Rahul Sharma (Ph: +91 98765 43210)\n"
                    "• **GDG (Google Developer Groups):** Coordinator - Priya Varma (Ph: +91 91234 56789)\n"
                    "• **Student Success Center:** Coordinator - Amit Kumar (Ph: +91 99887 76655)\n"
                    "• **Dance Club:** Coordinator - Neha Reddy (Ph: +91 94433 22110)\n"
                    "• **Music Club:** Coordinator - Rohit Verma (Ph: +91 95544 33221)\n"
                    "• **Drone Club:** Coordinator - Karthik Nair (Ph: +91 96655 44332)\n"
                    "• **Robotics Club:** Coordinator - Sneha Rao (Ph: +91 97766 55443)\n\n"
                    "Type **'menu'** to return to main options."
                )
            else:
                return "No worries! Type **'menu'** to return to main options."

        # 2. Flexible Global Navigation & Button Matchers
        if any(w in msg_lower for w in ["menu", "main menu"]) or "🏠" in message:
            user_states[clean_email] = "main_menu"
            return (
                "Welcome to Vishnu Institute of Technology IT Helpdesk! Please select an option below:\n\n"
                "1️⃣ **Create a Support Ticket**\n"
                "2️⃣ **Retrieve College Info**\n"
                "3️⃣ **Display Active Tickets (Live DB Query)**\n"
                "4️⃣ **Reset Portal Password**\n"
                "5️⃣ **Explore Campus Clubs & Join**\n"
                "6️⃣ **Facilities & Spots**\n"
                "7️⃣ **Food & Canteens**\n"
                "8️⃣ **Faculty & Placement Contacts**\n"
                "9️⃣ **Placement Statistics (2021-2026)**\n"
                "🔟 **Official College Web Portals**\n"
                "1️⃣1️⃣ **Smart Campus Outing Procedure**"
            )

        # Explicit Match for Creating a Support Ticket
        if msg_lower == "1" or ("create" in msg_lower and "ticket" in msg_lower):
            user_states[clean_email] = "creating_ticket_category"
            return (
                "🎫 **Create Support Ticket**\n"
                "Please select the category of your issue:\n\n"
                "1. Academic\n"
                "2. Hostel\n"
                "3. Library\n"
                "4. Placement\n"
                "5. Fee\n"
                "6. IT Support\n"
                "7. Examination\n"
                "8. Administration\n\n"
                "Type the category name or number."
            )

        # Explicit Match for Viewing/Displaying Active Tickets
        if msg_lower == "3" or any(w in msg_lower for w in ["my tickets", "active tickets", "view tickets"]):
            user_states[clean_email] = "main_menu"
            if not student:
                return f"⚠️ Student profile not found for `{clean_email}`. Please re-login.\n\nType **'menu'** to return."
            
            tickets = db.query(Ticket).filter(Ticket.student_id == student.id).all()
            active_tickets = [t for t in tickets if t.status not in ["Resolved", "Closed"]]
            
            if not active_tickets:
                return f"🔍 **Database Query Result:** Found **0 active tickets** for student `{student.name}` ({student.email}).\n\nType **'menu'** to return to main options."
            
            response_str = f"🔍 **Live Database Query Result for {student.name}:**\n\n"
            for t in active_tickets:
                response_str += f"• **Ticket #{t.id}** [{t.status}] - **{t.category}**: {t.description}\n"
            response_str += "\nType **'menu'** to return to main options."
            return response_str

        # College Info Match
        if msg_lower == "2" or "college info" in msg_lower or "📚" in message:
            user_states[clean_email] = "main_menu"
            return (
                "📚 **College Information Submenu**\n"
                "Select a topic below:\n\n"
                "• 1. Academics & Attendance\n"
                "• 2. Hostel & Mess Info\n"
                "• 3. Placement Stats (2021-2026 Batch Wise)\n"
                "• 4. Library Timings\n"
                "• 5. Examination Details\n"
                "• 6. Fee Counter\n"
                "• 7. IT & Wi-Fi Support\n"
                "• 8. EAPCET Cutoffs & Admissions\n\n"
                "Type the topic name or number."
            )

        # Password Reset Match
        if msg_lower == "4" or any(w in msg_lower for w in ["password", "reset"]):
            user_states[clean_email] = "reset_pwd_old"
            return "🔐 **Portal Password Reset**\nPlease enter your **current password**:"

        # Direct Mess Timings Override
        if any(term in msg_lower for term in ["mess timing", "mess timings", "food timing", "breakfast time", "lunch time", "dinner time", "hostel mess"]):
            user_states[clean_email] = "main_menu"
            return (
                "🍽️ **Hostel Mess Timings & Details:**\n"
                "• **Breakfast:** 7:30 AM – 9:30 AM\n"
                "• **Lunch:** 12:00 PM – 2:00 PM\n"
                "• **Snacks:** 4:30 PM – 5:30 PM\n"
                "• **Dinner:** 7:30 PM – 9:30 PM\n\n"
                "Type **'menu'** to return to main options."
            )

        # Direct Gym / Fitness Location Override
        if any(term in msg_lower for term in ["gym", "fitness", "workout", "where is gym"]):
            user_states[clean_email] = "main_menu"
            return (
                "🏢 **Gym Location:**\n"
                "The fully equipped modern gym and fitness center is located near the **Cyber Zone**.\n\n"
                "Type **'menu'** to return to main options."
            )

        # Direct FAQ Category Overrides returning clean answers without headers
        if any(term in msg_lower for term in ["hall ticket", "duplicate hall ticket", "exam branch", "revaluation"]):
            user_states[clean_email] = "main_menu"
            exam_data = FAQ_DATA.get("examination", [{}])[0]
            answer_text = exam_data.get('answer', '')
            return f"{answer_text}\n\nType **'menu'** to return to main options."

        if any(term in msg_lower for term in ["room change", "hostel room", "warden", "room allocation"]):
            user_states[clean_email] = "main_menu"
            hostel_data = FAQ_DATA.get("hostel", [{}])[0]
            answer_text = hostel_data.get('answer', '')
            return f"{answer_text}\n\nType **'menu'** to return to main options."

        if any(term in msg_lower for term in ["check results", "check my results", "how to check results", "exam results"]):
            user_states[clean_email] = "main_menu"
            exam_data = FAQ_DATA.get("examination", [{}])
            target_answer = "Semester examination results can be officially checked through the dedicated results portal at vishnu.ac.results."
            for item in exam_data:
                if "results" in item.get("question", "").lower():
                    target_answer = item.get("answer")
                    break
            return f"{target_answer}\n\nType **'menu'** to return to main options."

        # Specific Check for EAMCET / Admission Documents
        if any(term in msg_lower for term in ["document", "docs", "certificates", "required docs", "admission documents"]):
            user_states[clean_email] = "main_menu"
            return (
                "📋 **Required Admission Documents for EAMCET/EAPCET:**\n"
                "1. EAMCET/EAPCET Rank Card & Hall Ticket\n"
                "2. Study Certificates (6th to 10+2)\n"
                "3. Transfer Certificate (TC)\n"
                "4. Income & Caste Certificates\n\n"
                "Type **'menu'** to return to main options."
            )

        # Specific Club Inquiry Match
        if any(w in msg_lower for w in ["music club", "dance club", "drone club", "robotics club", "e-cell", "gdg", "student success center"]):
            user_states[clean_email] = "main_menu"
            if "music" in msg_lower:
                return (
                    "🎵 **Music Club Details:**\n"
                    "• **Coordinator:** Rohit Verma (Ph: +91 95544 33221)\n"
                    "• **How to Join:** Express your interest during annual club recruitments or contact the coordinator directly to audition or register.\n\n"
                    "Type **'menu'** to return to main options."
                )
            elif "dance" in msg_lower:
                return (
                    "💃 **Dance Club Details:**\n"
                    "• **Coordinator:** Neha Reddy (Ph: +91 94433 22110)\n"
                    "• **How to Join:** Attend annual club auditions and recruitment drives announced on department boards.\n\n"
                    "Type **'menu'** to return to main options."
                )
            elif "drone" in msg_lower:
                return (
                    "🛸 **Drone Club Details:**\n"
                    "• **Coordinator:** Karthik Nair (Ph: +91 96655 44332)\n"
                    "• **How to Join:** Register during tech-club recruitments or contact the coordinator.\n\n"
                    "Type **'menu'** to return to main options."
                )
            elif "robotics" in msg_lower:
                return (
                    "🤖 **Robotics Club Details:**\n"
                    "• **Coordinator:** Sneha Rao (Ph: +91 97766 55443)\n"
                    "• **How to Join:** Join during technical chapter recruitments to participate in hardware and bot-building workshops.\n\n"
                    "Type **'menu'** to return to main options."
                )
            elif "e-cell" in msg_lower or "ecell" in msg_lower:
                return (
                    "💡 **E-Cell (Entrepreneurship Cell):**\n"
                    "• **Coordinator:** Rahul Sharma (Ph: +91 98765 43210)\n"
                    "• **How to Join:** Participate in pitch events and startup ideathons during recruitment windows.\n\n"
                    "Type **'menu'** to return to main options."
                )
            elif "gdg" in msg_lower:
                return (
                    "🌐 **GDG (Google Developer Groups):**\n"
                    "• **Coordinator:** Priya Varma (Ph: +91 91234 56789)\n"
                    "• **How to Join:** Register during developer chapter orientation drives.\n\n"
                    "Type **'menu'** to return to main options."
                )

        # Explore Clubs General Match
        if msg_lower == "5" or "club" in msg_lower:
            user_states[clean_email] = "club_interest"
            return (
                "🎉 **Explore Campus Clubs & Chapters:**\n"
                "• **Technical Chapters**: E-Cell, GDG, Student Success Center\n"
                "• **Cultural & Hobby Clubs**: Dance, Music, Drone, and Robotics Clubs\n\n"
                "Would you like to see the official contact details and coordinators for all campus clubs? (Type **'yes'** or **'no'**)"
            )

        # Facilities Match
        if msg_lower == "6" or "facilities" in msg_lower:
            user_states[clean_email] = "main_menu"
            return (
                "🏢 **Campus Facilities & Spots:**\n"
                "• Digital Library & Normal Library\n"
                "• Movie theatre & Swimming pool\n"
                "• Peaceful Parks & Tea Leaf spot\n"
                "• Cyber Zone & Gym\n"
                "• Playground & Cricket Ground\n"
                "• Squash Court & Tennis Court\n"
                "• Snacks Zone & campus Temple for divine vibes\n\n"
                "Type **'menu'** to return to main options."
            )

        # Food Match
        if msg_lower == "7" or any(w in msg_lower for w in ["food", "canteen"]):
            user_states[clean_email] = "main_menu"
            return (
                "🍽️ **Food & Canteen Spots:**\n"
                "• **Canoe and Cuisine**: Famous for delicious biryanis\n"
                "• **Tea Leaf**: Refreshing tea and hot beverages\n"
                "• **Juice Corner**: Fresh fruit juices\n"
                "• **Temple Square & Central Square**: Quick snacks and bites\n"
                "• **Fresh Choice Bakery**: Birthday cakes and pastries\n"
                "• **Milk Parlour**: Fresh milk and dairy products\n\n"
                "Type **'menu'** to return to main options."
            )

        # Faculty Match
        if msg_lower == "8" or "faculty" in msg_lower:
            user_states[clean_email] = "main_menu"
            return (
                "👥 **Faculty & Placement Contacts:**\n"
                "• **Placements Related**: Contact the Training & Placement Office (TPO)\n"
                "• **Permissions & Academic Mentorship**: Contact your department HOD or assigned mentor\n\n"
                "Type **'menu'** to return to main options."
            )

        # Placement Statistics Match
        if msg_lower == "9" or "placements" in msg_lower or "placement" in msg_lower or "stats" in msg_lower or "📈" in message:
            user_states[clean_email] = "main_menu"
            return (
                "📈 **Batch-wise Placement Statistics (2021 - 2026):**\n"
                "• **2026 Batch**: 1000+ placements (Ongoing)\n"
                "• **2025 Batch**: 1250+ placements\n"
                "• **2024 Batch**: 1300+ placements\n"
                "• **2023 Batch**: 1400+ placements\n"
                "• **2022 Batch**: 1200+ placements\n"
                "• **2021 Batch**: 1100+ placements\n\n"
                "Type **'menu'** to return to main options."
            )

        # Web Portals Match
        if msg_lower == "10" or "portal" in msg_lower or "website" in msg_lower:
            user_states[clean_email] = "main_menu"
            return (
                "🌐 **Official College Web Portals:**\n"
                "• **vishnu.ac.in**: Used for attendance records, student profiles, and fee-related details.\n"
                "• **vishnu.ac.results**: Used for checking semester examination results.\n"
                "• **vishnulearning.com**: Used for semester study materials, lecture PDFs, quizzes, and assignments.\n"
                "• **vedic.dev**: Detailed student profiles for placements, mock interviews, and technical guidance. College administrators also communicate student notices via this website.\n\n"
                "Type **'menu'** to return to main options."
            )

        # Smart Campus Outing Procedure Match
        if msg_lower == "11" or "outing" in msg_lower or "smart campus" in msg_lower or "process" in msg_lower:
            user_states[clean_email] = "main_menu"
            return (
                "🚶 **Smart Campus Hostel Outing Procedure:**\n"
                "1. Open the **Smart Campus App**.\n"
                "2. Select **Outing** and choose between **General Outing** or **Local Outing**.\n"
                "3. Fill in all required details: Date, Reason, Out Time, In Time, and companion consent.\n"
                "4. **Parent Approval**: An automated WhatsApp message or call is sent to your parent/guardian to approve or decline.\n"
                "5. **HOD Approval**: Once approved by parents, your department HOD reviews and approves/declines based on regulations.\n"
                "6. **Warden Approval**: Head Warden gives final authorization.\n"
                "7. **Security Check-out**: Scan your pass at campus security to check out (parents receive a confirmation SMS/WhatsApp with date and time).\n"
                "8. **Return**: The exact same security scan procedure is repeated upon re-entering the campus.\n\n"
                "Type **'menu'** to return to main options."
            )

        # Examination Results Portal Link Match
        if any(w in msg_lower for w in ["result link", "results link", "exam link"]):
            user_states[clean_email] = "main_menu"
            return (
                "🌐 **Semester Examination Results Portal:**\n"
                "You can check your semester examination results directly on the official portal:\n"
                "• **Portal Link / Name**: `vishnu.ac.results`\n\n"
                "Type **'menu'** to return to main options."
            )

        if "eapcet" in msg_lower or "eamcet" in msg_lower or "admission" in msg_lower:
            user_states[clean_email] = "main_menu"
            eapcet_data = FAQ_DATA.get("eapcet", [{}])[0]
            return f"{eapcet_data.get('answer', '')}\n\nType **'menu'** to return to main options."

        # Smart JSON FAQ Dataset Scanner (Returns clean answer text without headers)
        for category, qa_list in FAQ_DATA.items():
            for item in qa_list:
                q_text = item.get("question", "").lower()
                keywords = [word for word in msg_lower.split() if len(word) > 3]
                if any(kw in q_text for kw in keywords) or msg_lower in q_text:
                    user_states[clean_email] = "main_menu"
                    answer_text = item.get('answer', '')
                    return f"{answer_text}\n\nType **'menu'** to return to main options."

        # 3. Fallback to LangChain PDF RAG Engine for Any General Question
        context = query_rag(message)
        if context and "I couldn't find exact guidelines" not in context:
            user_states[clean_email] = "main_menu"
            cleaned_text = context.replace("", "").strip()
            paragraphs = [p.replace("\n", " ").strip() for p in cleaned_text.split("\n\n") if p.strip()]
            formatted_body = "\n\n".join(paragraphs)
            return f"{formatted_body}\n\nType **'menu'** to return to main options."

        # 4. Final Fallback if nothing matches
        user_states[clean_email] = "main_menu"
        return "I didn't quite catch that. Please type **'menu'** to see the main options."

    except Exception as e:
        return f"An error occurred: {str(e)}\n\nType **'menu'** to restart."
    finally:
        db.close()