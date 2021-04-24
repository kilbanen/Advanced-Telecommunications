import firebase from 'firebase/app'
import 'firebase/auth'
import 'firebase/firestore'

// firebase init - add your own config here
const firebaseConfig = {
  apiKey: "AIzaSyD6Qc_MBAHMNwbUSl39Poe0gs4b3Uo1g1E",
  authDomain: "securing-the-cloud-a266a.firebaseapp.com",
  projectId: "securing-the-cloud-a266a",
  storageBucket: "securing-the-cloud-a266a.appspot.com",
  messagingSenderId: "32183504818",
  appId: "1:32183504818:web:3d7e30076e53df0053deab"
}
firebase.initializeApp(firebaseConfig)

// utils
const db = firebase.firestore()
const auth = firebase.auth()

// collection references
const usersCollection = db.collection('users')
const postsCollection = db.collection('posts')
const commentsCollection = db.collection('comments')
const likesCollection = db.collection('likes')

// export utils/refs
export {
  db,
  auth,
  usersCollection,
  postsCollection,
  commentsCollection,
  likesCollection
}
