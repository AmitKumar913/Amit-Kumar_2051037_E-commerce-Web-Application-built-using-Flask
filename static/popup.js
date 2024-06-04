
//   // Get the modal
//   var modal = document.getElementById("myModal");

//   // Get the button that opens the modal
//   var btn = document.getElementById("openModalBtn");

//   // Get the <span> element that closes the modal
//   var span = document.getElementsByClassName("close")[0];

//   // When the user clicks the button, open the modal
//   btn.onclick = function() {
//       modal.style.display = "block";
//   }

//   // When the user clicks on <span> (x), close the modal
//   span.onclick = function() {
//       modal.style.display = "none";
//   }

//   // When the user clicks anywhere outside of the modal, close it
//   window.onclick = function(event) {
//       if (event.target == modal) {
//           modal.style.display = "none";
//       }
//   }
// Get the update modal
var updateModal = document.getElementById("updateModal");

// Get the delete modal
var deleteModal = document.getElementById("deleteModal");

// Get the button that opens the update modal
var openUpdateModalBtn = document.getElementById("openUpdateModalBtn");

// Get the button that opens the delete modal
var openDeleteModalBtn = document.getElementById("openDeleteModalBtn");

// Get the <span> elements that close the modals
var closeButtons = document.querySelectorAll(".close");

// When the user clicks the update button, open the update modal
openUpdateModalBtn.onclick = function() {
    updateModal.style.display = "block";
}

// When the user clicks the delete button, open the delete modal
openDeleteModalBtn.onclick = function() {
    deleteModal.style.display = "block";
}

// When the user clicks on <span> (x) in any modal, close the modal
closeButtons.forEach(function(button) {
    button.onclick = function() {
        updateModal.style.display = "none";
        deleteModal.style.display = "none";
    }
});

// When the user clicks anywhere outside of any modal, close it
window.onclick = function(event) {
    if (event.target == updateModal || event.target == deleteModal) {
        updateModal.style.display = "none";
        deleteModal.style.display = "none";
    }
}

