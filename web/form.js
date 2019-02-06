// measurement data object, later filled and pushed to the api
let dataModel = {
  h: [],
  dd: [],
  ud: []
}
let allData = JSON.parse(JSON.stringify(dataModel)), savedData = null

let previousDownKey, currentUpKey, currentDownKey, // keys needed for measurements
  wordInputWrapper, wordInput, wordDisplay, repetitionDisplay, distanceMetricDropdown // DOM elements

let keystrokeTestID, quizID, courseId, studentHasRecord, studentHasImage // other global data variables

// default settings
let word = 'testtest', allRepetitions = 2, remainingRepetitions = 2

// other variables, needed for computations and checks
let currentIndexWritten = 0, hDurations = [], ddDurations = [], udDurations = [], keyTimes = {}

const getUrlParam = (name) => {
  url = window.location.href
  name = name.replace(/[\[\]]/g, '\\$&')
  let regex = new RegExp('[?&]' + name + '(=([^&#]*)|&|#|$)')
  let results = regex.exec(url)
  if (!results) return null
  if (!results[2]) return ''
  return decodeURIComponent(results[2].replace(/\+/g, ' '))
}

const measureTimes = (e) => {
  recordDownUpDuration(e)
}

const recordDownUpDuration = (e) => {
  const kc = e.keyCode
  if (kc === 27 || kc === 16 || kc === 17 || kc === 18 || kc === 91 || kc === 93) return // not looking at shifts, esc, alt and ctrl

  // If the key DOWN-UP pattern wasn't yet recorded, initialize empty object
  if (!keyTimes[kc]) {
    keyTimes[kc] = {}
  }

  if (e.type === 'keydown') {

    currentDownKey = { key: keyCodes[kc], timestamp: Date.now() }

    // Record key down press timestamp if key is not yet being held
    if (!e.repeat) {
      keyTimes[kc].lastDown = Date.now()

      recordDownDownDuration(e) // compute DOWN-DOWN duration between this and the previous keydown
      recordUpDownDuration(e) // compute UP-DOWN duration between this and the previous keyup
    }

  } else if (e.type === 'keyup') {

    // Record key up press timestamp
    keyTimes[kc].lastUp = Date.now()

    const duration = keyTimes[kc].lastUp - keyTimes[kc].lastDown
    if (!isNaN(duration)) {
      hDurations.push({ key: keyCodes[kc], duration })
    } else {
      console.log(1)
      resetAllVariables()

      wordInput.blur()
      alert("restart typing")
      wordInput.value = ''
      wordInput.focus()
    }

    currentUpKey = { key: keyCodes[kc], timestamp: Date.now() }
    // after DOWN-UP pattern is complete, clear values for another possible measure
    keyTimes[kc] = {}

    checkCorrectCharacterWritten(e)
  }
}

const recordDownDownDuration = (e) => {
  if (previousDownKey) {
    ddDurations.push(
      {
        key1: previousDownKey.key,
        key2: currentDownKey.key,
        duration: Date.now() - previousDownKey.timestamp
      }
    )
  }

  previousDownKey = currentDownKey
}

const recordUpDownDuration = (e) => {
  if (currentUpKey) {
    udDurations.push(
      {
        key1: currentUpKey.key,
        key2: currentDownKey.key,
        duration: Date.now() - currentUpKey.timestamp
      }
    )
  }
}

// check if we're writing the correct letter, else restart
const checkCorrectCharacterWritten = (e) => {

  if (wordInput.value.charAt(currentIndexWritten) === word.charAt(currentIndexWritten)) {
    currentIndexWritten++
  } else {
    console.log(2)
    resetAllVariables()

    wordInput.blur()
    alert('wrong character pressed, restart typing')
    wordInput.value = ''
    wordInput.focus()
  }
  checkIfEndOfInput(e)
}

const checkIfEndOfInput = () => {
  if (wordInput.value.length === word.length) {
    // check if everything was recorded
    if (ddDurations.length === hDurations.length - 1 && udDurations.length === hDurations.length - 1) {
      remainingRepetitions--
      allData.h.push(hDurations)
      allData.dd.push(ddDurations)
      allData.ud.push(udDurations)
    } else {
      wordInput.blur()
      alert('you were typing too fast, restart typing')
      wordInput.value = ''
      wordInput.focus()
    }
    console.log(3)
    resetAllVariables()
  }
  checkIfEndOfTest()
  repetitionDisplay.innerHTML = remainingRepetitions
}

const checkIfEndOfTest = () => {
  if (remainingRepetitions === 0) {
    const mode = parseInt(document.querySelector('input[name="mode"]:checked').value)

    if (mode === 0) { // registration mode
      savedData = allData
      alert('You must now switch the mode to "Comparing to previously registered pattern"')
    } else { // comparison mode

      const formData = new FormData()
      const registeredData = JSON.stringify(convertToCSV(savedData))
      const currentData = JSON.stringify(convertToCSV(allData))

      console.log("registered: ", registeredData)
      console.log("current: ", currentData)

      formData.append('user_id', window.currentUser)
      formData.append('quiz_id', quizID)
      formData.append('timing_matrix_registered', registeredData)
      formData.append('timing_matrix_current', currentData)

      distanceMetric = distanceMetricDropdown.value

      fetch('http://localhost:5000/' + distanceMetric, { method: "POST", body: formData })
        .then((res) => res.json())
        .then((result) => {
          let accept = confirm("Computed distance is: " + result.distance + ". Do you wish to test again?")
          if (accept) {
            window.location.reload()
          }
        })
    }
    resetAllVariables()
    resetAllData()
  }
}

const resetAllData = () => {
  allData = JSON.parse(JSON.stringify(dataModel))
}

const resetRepetitions = () => {
  remainingRepetitions = allRepetitions
  repetitionDisplay.innerHTML = remainingRepetitions
}

const resetAllVariables = () => {
  wordInput.value = ''
  currentIndexWritten = 0

  hDurations = []; ddDurations = []; udDurations = [];
  previousDownKey = null; currentDownKey = null; currentUpKey = null;
}

const convertToCSV = (kd) => {

  let outputMatrix = []

  // loop through all sessions
  for (let sessionNumber = 0; sessionNumber < kd.h.length; sessionNumber++) {
    let holdEntrySession = kd.h[sessionNumber]
    let outputVector = []

    for (let holdNumber = 0; holdNumber < holdEntrySession.length; holdNumber++) {
      let keyPress = holdEntrySession[holdNumber]
      let nextKeyPress

      // add the hold duration
      outputVector.push(keyPress.duration)

      // DD and UD are of the current key and the next one (if it exists)
      if (holdNumber !== holdEntrySession.length - 1) {

        nextKeyPress = holdEntrySession[holdNumber + 1]

        outputVector.push(kd.dd[sessionNumber][holdNumber].duration)
        outputVector.push(kd.ud[sessionNumber][holdNumber].duration)
      }
    }
    outputMatrix.push(outputVector)
  }

  return outputMatrix
}

window.onload = () => {

  // get the DOM objects we need to change/record
  wordDisplay = document.getElementById('wordDisplay')
  wordInput = document.getElementById('wordInput')
  repetitionDisplay = document.getElementById('remainingRepetitions')

  let comparisonRadio = document.getElementById('comparison-radio')
  distanceMetricDropdown = document.getElementById('distance')

  wordDisplay.innerHTML = word
  repetitionDisplay.innerHTML = remainingRepetitions

  wordInput.onkeydown = wordInput.onkeyup = measureTimes

  comparisonRadio.onclick = resetRepetitions
}