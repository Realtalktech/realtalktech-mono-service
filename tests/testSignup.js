const signup = (body) => {
  const url = `http://ec2-3-95-180-146.compute-1.amazonaws.com/signup`
  const params = {
    method: "PUT",
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body)
  }
  fetch(url, params).then(res => {
    return res.json()
  }).then(json => {
    console.log("GOOD-signup", json)
    // dispatch({type: "POSTS_SUCCESS", payload: json})
  }).catch((err) => {
    console.log("ERR-signup", err)
  })
}
const bodySignup = {
  fullname: 'robert',
  username: 'smith',
  email: 'rob1@gmail.com',
  password: 'pass123',
  techStack: [],
  currentCompany: "HERE",
  industryInvolvement: [],
  workCategories: [],
  linkedinUrl: "www.linedin.com/rob1",
  bio: "alksdjflsd",
  interestAreas: [],
}
signup(bodySignup)




const DEFAULT_TOKEN = "123423ff";

const login = (username, password, token = DEFAULT_TOKEN) => {
  const url = `http://ec2-3-95-180-146.compute-1.amazonaws.com/login`
  const params = {
    method: "POST",
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({
      username,
      password,
    })
  }
  fetch(url, params).then(res => {
    return res.json()
  }).then(json => {
    console.log("GOOD-login", json)
    // dispatch({type: "POSTS_SUCCESS", payload: json})
  }).catch((err) => {
    console.log("ERR-login", err)
  })
}
login("test_user1", "test123")