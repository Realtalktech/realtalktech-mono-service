const signup = (body) => {
  const url = `http://ec2-3-95-180-146.compute-1.amazonaws.com/signup`;
  const params = {
    method: "PUT",
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body)
  };
  return fetch(url, params) // Return the fetch promise
    .then(res => res.json())
    .then(json => {
      console.log("GOOD-signup", json);
      // dispatch({type: "POSTS_SUCCESS", payload: json});
    }).catch((err) => {
      console.log("ERR-signup", err);
    });
};

const bodySignup = {
  fullname: 'asd',
  username: 'asd',
  email: 'asd@gmail.com',
  password: 'asd',
  techStack: [],
  currentCompany: "asd",
  industryInvolvement: ["Automation", "Cannabis"],
  workCategories: ["Marketing"],
  bio: "asd",
  interestAreas: ["Analytics Tools & Software", "Commerce", "Design"],
};

const DEFAULT_TOKEN = "123423ff";

const login = (username, password, token = DEFAULT_TOKEN) => {
  const url = `http://ec2-3-95-180-146.compute-1.amazonaws.com/login`;
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
  };
  return fetch(url, params) // Return the fetch promise
    .then(res => res.json())
    .then(json => {
      console.log("GOOD-login", json);
      // dispatch({type: "POSTS_SUCCESS", payload: json});
    }).catch((err) => {
      console.log("ERR-login", err);
    });
};

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Function to control the flow
const executeSignupAndLogin = async (bodySignup) => {
  await signup(bodySignup); // Wait for signup to finish
  await sleep(5000); // Wait for 5 seconds
  login('smith', 'pass123'); // Then login
};

executeSignupAndLogin(bodySignup); // Call the function
