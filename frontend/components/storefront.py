import streamlit as st
from config import OTC_PRODUCTS

def render_storefront():
    st.title("🛒 Pharmacy Storefront")
    st.write("Browse over-the-counter medications. All checkouts are reviewed by our AI Safety Agent.")

    if st.button("← Back to Chat"):
        st.session_state.ui_phase = "chatting"
        st.rerun()

    # --- FETCH INVENTORY ---
    # SWAP THIS -- currently using static OTC_PRODUCTS from config.py
    # When backend ready, replace with:
    #   from services.api_client import call_inventory
    #   products = call_inventory()
    # Delete dummy line above when swapping.
    products = OTC_PRODUCTS 

    col_products, col_cart = st.columns([2, 1])

    with col_products:
        st.subheader("Available Products")
        grid_cols = st.columns(2)
        
        for index, product in enumerate(products):
            with grid_cols[index % 2]:
                with st.container(border=True):
                    st.markdown(f"**{product['name']}**")
                    st.write(f"Price: ${product['price']:.2f}")
                    st.write(f"Category: {product['category']}")
                    
                    if product['stock'] <= 0:
                        st.error("Out of Stock")
                    elif product['restricted']:
                        st.warning("Prescription Required")
                        if st.button("Upload Rx", key=f"rx_{index}"):
                            st.session_state.pending_prescription = product['name']
                            st.session_state.ui_phase = "prescription_upload"
                            st.rerun()
                    else:
                        st.success(f"In Stock: {product['stock']}")
                        if st.button("Add to Cart", key=f"add_{index}"):
                            # --- LOGICAL CART: Group duplicates ---
                            found = False
                            for item in st.session_state.cart:
                                if item['name'] == product['name']:
                                    item['quantity'] += 1
                                    found = True
                                    break
                            
                            if not found:
                                new_item = product.copy()
                                new_item['quantity'] = 1
                                st.session_state.cart.append(new_item)
                            
                            st.rerun()

    with col_cart:
        st.subheader("Your Cart")
        if not st.session_state.cart:
            st.info("Cart is empty.")
        else:
            total = 0.0
            for item in st.session_state.cart:
                item_total = item['price'] * item['quantity']
                st.write(f"- **{item['name']}** (x{item['quantity']}) : ${item_total:.2f}")
                total += item_total
            
            st.markdown("---")
            st.markdown(f"**Total: ${total:.2f}**")
            
            # 1. Generate Payment Link Button
            if st.button("💳 Generate Payment Link", use_container_width=True, type="primary"):
                from services.api_client import call_create_payment_link
                name = st.session_state.get("patient_name", "Guest")
                
                with st.spinner("Connecting to Paypal..."):
                    link = call_create_payment_link(total, name)
                    if link:
                        st.session_state.payment_link = link
                    else:
                        st.error("Payment gateway unavailable.")
                        
            # 2. Show the actual Pay button if the link exists
            if st.session_state.get("payment_link"):
                st.success("Payment link generated securely!")
                
                # Streamlit's native link button opens nicely in a new tab
                st.link_button(
                    "Redirect to Paypal Checkout ↗", 
                    st.session_state.payment_link, 
                    type="secondary", 
                    use_container_width=True
                )
                
                # 3. Once paid, they click this to finalize and get AI review
                if st.button("✅ I have completed the payment", use_container_width=True, type="primary"):
                    cart_items = ", ".join([f"{item['name']} x{item['quantity']}" for item in st.session_state.cart])
                    age = st.session_state.get('patient_age', 'unknown')
                    
                    checkout_prompt = (
                        f"I am {age} years old. I have just paid for the following OTC medications: {cart_items}. "
                        f"Please finalize this transaction, provide dosage instructions, and check for contraindications."
                    )
                    
                    # Clear cart and payment link, trigger chat
                    st.session_state.cart = []
                    st.session_state.payment_link = None
                    st.session_state.checkout_prompt = checkout_prompt
                    st.session_state.ui_phase = "chatting"
                    st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Clear Cart", use_container_width=True):
                st.session_state.cart = []
                st.session_state.payment_link = None # Clear link too
                st.rerun()