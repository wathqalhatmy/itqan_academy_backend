function markAllAttendance(status) {
  const selects = document.querySelectorAll('.attendance-select');
  selects.forEach(select => {
    select.value = status;
  });
}
