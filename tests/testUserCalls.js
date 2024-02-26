const DEFAULT_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MDg4MzQxOTgsImlhdCI6MTcwODgyMzM5OCwic3ViIjo3fQ.eB-fdQAOKmcfGD0cObsJGCHpr5edxGhDg2knhMLNoXM';

// User -------------------------------------

const fetchUser = (username, token = DEFAULT_TOKEN) => {
  const url = `http://ec2-44-201-178-172.compute-1.amazonaws.com/user/${username}`
  const params = {
    method: "GET",
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  }
  fetch(url, params).then(res => {
    return res.text()
  }).then(json => {
    console.log("GOOD-fetchUser", json)
    // dispatch({type: "POSTS_SUCCESS", payload: json})
  }).catch((err) => {
    console.log("ERR-fetchUser", err)
  })
}
fetchUser('AP100')

const endorseUser = (body, token = DEFAULT_TOKEN) => {
  const url = `http://ec2-3-95-180-146.compute-1.amazonaws.com/endorse`
  const params = {
    method: "PUT",
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(body)
  }
  fetch(url, params).then(res => {
    return res.json()
    // return res.text()
  }).then(json => {
    console.log("GOOD-endorseUser", json)
    // dispatch({type: "POSTS_SUCCESS", payload: json})
  }).catch((err) => {
    console.log("ERR-endorseUser", err)
  })
}

const bodyEndorse = {
  endorserUserId: 1,
  endorseeUsername: "msmith21",
  vendorId: 1,
}
// endorseUser(bodyEndorse)