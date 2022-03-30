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
			data: {"subscription_token": JSON.stringify(subscription)}
		})
	} else {
		$.ajax({
			type:"DELETE",
			url:'/subscription/'
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
			alert(error)
		});
} else {
	console.warn('Push meapplicationServerPublicKeyssaging is not supported');
	pushButton.textContent = 'Benachrichtigung nicht unterstützt';
	pushButton.disabled = ture;
}


$(document).ready(function(){
	$.ajax({
		type:"GET",
		url:'/subscription/',
		success:function(response){
			localStorage.setItem('applicationServerPublicKey',response.public_key);
		}
	})
	$.ajax({
		type:"GET",
		url:'/api/data',
		success:function(response){
			const devicelist = document.querySelector('#devices');
			const openedlist = document.querySelector('#opened');

			removeAllChildNodes(devicelist)
			removeAllChildNodes(openedlist)

			response.devices.forEach(device => {
				var jdevice = JSON.parse(device);
				var tempDevice = document.getElementsByTagName("template")[0];

				var clone = tempDevice.content.cloneNode(true);
				var name = clone.querySelector("#name");
				var lastSignal = clone.querySelector("#lastsignal");

				name.innerHTML = jdevice.name == null ? "Unbenannt" : jdevice.name;
				var date = jdevice.lastSignal == null ? null : new Date(jdevice.lastSignal);

				if (!date){
					lastSignal.style.color = "red";
					lastSignal.innerHTML = "-";
				}
				else{
					deltadate = (new Date.now() - date) / 60000;
					if (deltadate > 1)
						lastSignal.style.color = "red";
					else
						lastSignal.style.color = "green";
					lastSignal.innerHTML = deltadate + "m";
				}
				devicelist.appendChild(clone);
			});

			response.opened.forEach(stamp => {
				var jstamp = JSON.parse(stamp);
				var tempStamp = document.getElementsByTagName("template")[1];
				var clone = tempStamp.content.cloneNode(true);
				var name = jstamp.name == null ? "Unbenannt" : jstamp.name;
				var entry = clone.querySelector("#entry");
				entry.innerHTML = name + ": " + jstamp.time;
				openedlist.appendChild(clone);
			});
		}
	})
});

function removeAllChildNodes(parent) {
    while (parent.firstChild) {
        parent.removeChild(parent.firstChild);
    }
}