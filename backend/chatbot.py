import os
from tools import reset_password, create_ticket, show_tickets, search_knowledge_base
from database import SessionLocal
from models import Student
from dotenv import load_dotenv

load_dotenv()
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# In-memory session state dictionary to track menu flows per user
user_states = {}

def process_chat_message(message: str, session_id: str) -> str:
    msg_lower = message.lower().strip()
    
    # Extract clean student identifier from message tag
    student_id = session_id
    if "[user email:" in msg_lower:
        try:
            parts = message.split("[User Email:")
            student_id = parts[1].split("]")[0].strip()
            message = parts[1].split("]")[1].strip()
            msg_lower = message.lower().strip()
        except Exception:
            pass

    current_state = user_states.get(session_id, "main_menu")

    # Global reset or menu command
    if msg_lower in ["hi", "hello", "menu", "start", "back", "home", "get started"]:
        user_states[session_id] = "main_menu"
        return (
            "Welcome to Vishnu Institute of Technology IT Helpdesk! Please select an option below:\n\n"
            "1️⃣ **Create a Support Ticket**\n"
            "2️⃣ **Retrieve College Info**\n"
            "3️⃣ **Display Active Tickets**\n"
            "4️⃣ **Reset Portal Password**"
        )

    # Expanded polite and conversational response handler (manners filter on separate lines)
    polite_keywords = ["thank", "thanks", "thx", "cool", "awesome", "great", "perfect", "super", "ok", "k", "fine", "sounds good", "got it", "alright"]
    if any(keyword == msg_lower or keyword in msg_lower for keyword in polite_keywords) and len(msg_lower) < 15:
        user_states[session_id] = "main_menu"
        return "You're very welcome! Glad I could help. Type **'menu'** whenever you need anything else."

    # --- STATE 1: MAIN MENU SELECTION ---
    if current_state == "main_menu":
        if "1" in msg_lower or "create" in msg_lower or "ticket" in msg_lower and "show" not in msg_lower:
            user_states[session_id] = "awaiting_ticket_desc"
            return "Please describe your issue (e.g., 'Hostel WiFi not working'):"
            
        elif "2" in msg_lower or "retrieve" in msg_lower or "college info" in msg_lower or "info" in msg_lower:
            user_states[session_id] = "rag_submenu"
            return (
                "📚 **College Information Submenu**\n"
                "Select a topic below:\n\n"
                "• **1. Library Timings**\n"
                "• **2. Fee Counter Details**\n"
                "• **3. Biometric Timings**\n"
                "• **4. Event Timings** (Vishnu Fiesta)\n"
                "• **5. EAPCET 2025 Cutoffs & Admissions**\n"
                "• **6. Placement & Transport**"
            )
            
        elif "3" in msg_lower or "display" in msg_lower or "show" in msg_lower or "active" in msg_lower or "my tickets" in msg_lower:
            user_states[session_id] = "main_menu"
            return show_tickets.invoke({"student_id": student_id})
            
        elif "4" in msg_lower or "reset" in msg_lower or "password" in msg_lower:
            user_states[session_id] = "awaiting_new_password"
            return "🔐 **Password Reset:**\nPlease enter your desired new password:"
            
        else:
            return search_knowledge_base.invoke(message)

    # --- STATE 2: RAG SUBMENU (College Info) ---
    elif current_state == "rag_submenu":
        user_states[session_id] = "main_menu"
        
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
                "2. Aadhar Card & Study Certificates (6th to 10+2)\n"
                "3. Transfer Certificate (TC)\n"
                "4. Income & Caste Certificates\n\n"
                "📍 **Admission Venue:** Ground floor of the main administrative block.\n\n"
                "Type **'menu'** to return to main options."
            )
            
        elif "placement" in msg_lower or "transport" in msg_lower or "6" in msg_lower:
            return "🚌 **Placement & Transport:**\nCRT training managed by T&P cell in the seminar hall. Bus routes cover Bhimavaram town from **7:30 AM to 5:30 PM**.\n\nType **'menu'** to return to main options."
            
        else:
            return f"{search_knowledge_base.invoke(message)}\n\nType **'menu'** to return to main options."

    # --- STATE 3: CREATING TICKET ---
    elif current_state == "awaiting_ticket_desc":
        user_states[session_id] = "main_menu"
        category = "Hostel WiFi" if "wifi" in msg_lower else "General Support"
        return create_ticket.invoke({"student_id": student_id, "category": category, "description": message})

    # --- STATE 4: UPDATING PASSWORD DIRECTLY ---
    elif current_state == "awaiting_new_password":
        user_states[session_id] = "main_menu"
        db = SessionLocal()
        try:
            student = db.query(Student).filter(Student.email == student_id.lower().strip()).first()
            if student:
                student.password = message.strip()
                db.commit()
                return f"SUCCESS: Your portal password has been updated successfully! You can now log in with your new password.\n\nType **'menu'** for main options."
            else:
                return "Error: Student account not found in database. Please log in again."
        except Exception as e:
            return f"Database error updating password: {str(e)}"
        finally:
            db.close()

    user_states[session_id] = "main_menu"
    return search_knowledge_base.invoke(message)