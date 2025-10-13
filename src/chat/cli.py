import argparse
from sqlalchemy.orm import Session
from src.database import SessionLocal
from src.chat.flows import CustomerFlow, SupplierFlow

class KcartBotCLI:
    def __init__(self):
        self.db = SessionLocal()
        self.current_flow = None
        self.user_type = None
    
    def start(self):
        """Start the CLI chatbot"""
        print("=" * 50)
        print("Welcome to KcartBot - Advanced AI Agri-Commerce Assistant")
        print("=" * 50)
        print("\nAre you a customer or supplier?")
        print("1. Customer")
        print("2. Supplier")
        print("3. Exit")
        
        while True:
            choice = input("\nEnter choice (1-3): ").strip()
            
            if choice == "1":
                self.user_type = "customer"
                self.current_flow = CustomerFlow(self.db)
                print("\nCustomer mode activated. How can I help you today?")
                self.chat_loop()
            elif choice == "2":
                self.user_type = "supplier"
                self.current_flow = SupplierFlow(self.db)
                print("\nSupplier mode activated. How can I assist your business?")
                self.chat_loop()
            elif choice == "3":
                print("Thank you for using KcartBot!")
                break
            else:
                print("Please enter 1, 2, or 3.")
    
    def chat_loop(self):
        """Main chat loop"""
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'back']:
                    print("Returning to main menu...")
                    break
                
                if self.user_type == "customer" and "deliver" in user_input.lower():
                    # Simulate order completion
                    if hasattr(self.current_flow, 'complete_order'):
                        response = self.current_flow.complete_order(
                            "2024-12-25",  # Default date
                            "Addis Ababa"  # Default location
                        )
                    else:
                        response = self.current_flow.handle_message(user_input)
                else:
                    response = self.current_flow.handle_message(user_input)
                
                print(f"\nKcartBot: {response}")
                
            except KeyboardInterrupt:
                print("\n\nReturning to main menu...")
                break
            except Exception as e:
                print(f"\nKcartBot: I encountered an error. Please try again. Error: {str(e)}")

def main():
    cli = KcartBotCLI()
    cli.start()

if __name__ == "__main__":
    main()