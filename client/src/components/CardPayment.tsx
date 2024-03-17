import React, {useState} from 'react';
import axios from 'axios';
import {useStripe, useElements, CardElement } from '@stripe/react-stripe-js';
import {API_URL} from "../constants/constant";
import CardInput from "./CardInput";

function CardPayment() {
  const [email, setEmail] = useState('');

  const stripe = useStripe();
  const elements = useElements();

  // const handleSubmitPay = async (e: React.MouseEvent<HTMLButtonElement>) => {
  const handleSubmitPay = async () => {

    if (!stripe || !elements) {
      // Stripe.js has not yet loaded.
      // Make sure to disable form submission until Stripe.js has loaded.
      return;
    }

    const cardElements = elements.getElement(CardElement);
    if (!cardElements) {
      return;
    }

    const res = await axios.post(`${API_URL}/api/create-payment-intent`, {email: email});

    const clientSecret = res.data['client_secret'];

    const result = await stripe.confirmCardPayment(clientSecret, {
      payment_method: {
        card: cardElements,
        billing_details: {
          email: email,
        },
      },
    });

    if (result.error) {
      // Show error to your customer (e.g., insufficient funds)
      console.log(result.error.message);
    } else {
      // The payment has been processed!
      if (result.paymentIntent.status === 'succeeded') {
        // Show a success message to your customer
        // There's a risk of the customer closing the window before callback
        // execution. Set up a webhook or plugin to listen for the
        // payment_intent.succeeded event that handles any business critical
        // post-payment actions.
        console.log('You got 500$!');
      }
    }
  };


  return (
    <div className="card">
      <div className="card-body">
        <h2 className={"card-title"}>Payment widget</h2>
        <input type="text" placeholder={"Email"} className={"input w-full"} onChange={(e) => setEmail(e.target.value)}/>
        <CardInput />
        <div>
          <button onClick={handleSubmitPay}>
            Pay
          </button>
        </div>
      </div>
    </div>
  );
}

export default CardPayment;