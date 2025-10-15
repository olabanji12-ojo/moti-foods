console.log("Cart.js loaded ✅");

// --- Add to Cart buttons on product page ---
let addToCartBtns = document.getElementsByClassName('add-to-cart');

for (let i = 0; i < addToCartBtns.length; i++) {
    addToCartBtns[i].addEventListener('click', () => {
        let product_id = addToCartBtns[i].dataset.productId;
        let action = addToCartBtns[i].dataset.action;

        updateUserOrder(product_id, action);
    });
}

// --- Quantity + / − and delete buttons on cart page ---
document.addEventListener('DOMContentLoaded', () => {
    const quantityBtns = document.querySelectorAll('.quantity-btn');
    const removeBtns = document.querySelectorAll('.remove-item');

    quantityBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const productId = btn.dataset.productId;
            const action = btn.dataset.action;
            updateUserOrder(productId, action);
        });
    });

    removeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const productId = btn.dataset.productId;
            updateUserOrder(productId, 'delete');
        });
    });
});

// --- Function to send update request ---
function updateUserOrder(productId, action) {
    console.log('Product ID:', productId);
    console.log('Action:', action); 

    let url = "/update_cart/";

    fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken,
        },
        body: JSON.stringify({ product_id: productId, action: action }),
    })
    .then((response) => response.json())
    .then((data) => {
        console.log("Cart updated:", data);

    // --- Update navbar + mobile cart count ---
        const cartItemsCountEls = document.querySelectorAll(".cart-items-count");
        cartItemsCountEls.forEach(el => {
            el.innerText = data.cart_count;
        });

        // --- Update cart summary count (right side of cart page) ---
        const cartSummaryEl = document.getElementById("cart-items");
        if (cartSummaryEl) {
            cartSummaryEl.innerText = data.cart_count;
        }

        const cartTotalEl = document.getElementById("cart-total");
        const cartTotalFinalEl = document.getElementById("cart-total-final");
        if (cartTotalEl) cartTotalEl.innerText = `$${data.cart_total.toFixed(2)}`;
        if (cartTotalFinalEl) cartTotalFinalEl.innerText = `$${data.cart_total.toFixed(2)}`;

        // --- Update product quantity ---
        const qtyEl = document.getElementById(`qty-${productId}`);
        if (qtyEl) qtyEl.innerText = data.quantity;

        // --- Update product total ---
        const totalEl = document.getElementById(`total-${productId}`);
        if (totalEl) totalEl.innerText = `$${data.item_total.toFixed(2)}`;

        // --- Remove cart item if quantity is 0 or deleted ---
        if (data.quantity === 0 || action === 'delete') {
            const cartItemEl = document.querySelector(`.cart-item[data-product-id="${productId}"]`);
            if (cartItemEl) cartItemEl.remove();
        }
    })
    .catch((error) => console.error("Error updating cart:", error));
}
