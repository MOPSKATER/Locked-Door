'use strict';

const pushButton = document.querySelector('#subscriber');

let isSubscribed = false;
let swRegistration = null;

function urlB64ToUint8Array(base64String) {
	const padding = '='.repeat((4 - base64String.length % 4) % 4);
	const base64 = (base64String + padding)
		.replace(/\-/g, '+')
		.replace(/_/g, '/');

	const rawData = window.atob(base64);
	const outputArray = new Uint8Array(rawData.length);

	for (let i = 0; i < rawData.length; ++i) {
		outputArray[i] = rawData.charCodeAt(i);
	}
	return outputArray;
}

function updateBtn() {
	if (Notification.permission === 'denied') {
		pushButton.textContent = 'Einen Moment';
		pushButton.disabled = true;
		updateSubscriptionOnServer(null);
		return;
	}

	if (isSubscribed) {
		pushButton.textContent = 'Werde nicht mehr Benachrichtigt';
	} else {
		pushButton.textContent = 'Werde Benachrichtigt';
	}

	pushButton.disabled = false;
}

function updateSubscriptionOnServer(subscription) {
	if (subscription) {
		$.ajax({
			type:"POST",
			url:'/subscription/',
			content_type: "application/json",
			data: {"subscription_token": JSON.stringify(subscription)},
			success:function(response){
				console.log("response",response);
				localStorage.setItem('applicationServerPublicKey',response.public_key);
			}
		})
	} else {
		$.ajax({
			type:"DELETE",
			url:'/subscription/',
			success:function(response){
				console.log("response",response);
				localStorage.removeItem('applicationServerPublicKey');('applicationServerPublicKey',response.public_key);
			}
		})
	}
}

function subscribeUser() {
	const applicationServerPublicKey = localStorage.getItem('applicationServerPublicKey');
	const applicationServerKey = urlB64ToUint8Array(applicationServerPublicKey);
	swRegistration.pushManager.subscribe({
			userVisibleOnly: true,
			applicationServerKey: applicationServerKey
		})
		.then(function(subscription) {
			updateSubscriptionOnServer(subscription)
			console.log('User is subscribed.');
			localStorage.setItem('sub_token',JSON.stringify(subscription));
			isSubscribed = true;

			updateBtn();
		})
		.catch(function(err) {
			console.log('Failed to subscribe the user: ', err);
			updateBtn();
		});
}

function unsubscribeUser() {
	swRegistration.pushManager.getSubscription()
		.then(function(subscription) {
			if (subscription) {
				return subscription.unsubscribe();
			}
		})
		.catch(function(error) {
			console.log('Error unsubscribing', error);
		})
		.then(function() {
			updateSubscriptionOnServer(null);

			console.log('User is unsubscribed.');
			isSubscribed = false;

			updateBtn();
		});
}

function initializeUI() {
	pushButton.addEventListener('click', function() {
		pushButton.disabled = true;
		if (isSubscribed) {
			unsubscribeUser();
		} else {
			subscribeUser();
		}
	});

	// Set the initial subscription value
	swRegistration.pushManager.getSubscription()
		.then(function(subscription) {
			isSubscribed = !(subscription === null);
			if (isSubscribed) {
				console.log('User IS subscribed.');
			} else {
				console.log('User is NOT subscribed.');
			}

			updateBtn();
		});
}

if ('serviceWorker' in navigator && 'PushManager' in window) {
	console.log('Service Worker and Push is supported');
	navigator.serviceWorker.register("/static/sw.js")
		.then(function(swReg) {
			console.log('Service Worker is registered', swReg);

			swRegistration = swReg;
			initializeUI();
		})
		.catch(function(error) {
			console.error('Service Worker Error', error);
		});
} else {
	console.warn('Push meapplicationServerPublicKeyssaging is not supported');
	pushButton.textContent = 'Push Not Supported';
}


$(document).ready(function(){
	$.ajax({
		type:"GET",
		url:'/subscription/',
		success:function(response){
			localStorage.setItem('applicationServerPublicKey',response.public_key);
		}
	})
});
