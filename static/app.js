function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', function() {
    document.addEventListener('click', function(e) {
        const likeBtn = e.target.closest('.like-btn');
        const dislikeBtn = e.target.closest('.dislike-btn');
        const answerLikeBtn = e.target.closest('.answer-like-btn');
        const answerDislikeBtn = e.target.closest('.answer-dislike-btn');
        const solutionBtn = e.target.closest('.mark-solution-btn');

        if (likeBtn) {
            e.preventDefault();
            handleVote(likeBtn, 'like');
        }

        if (dislikeBtn) {
            e.preventDefault();
            handleVote(dislikeBtn, 'dislike');
        }

        if (answerLikeBtn) {
            e.preventDefault();
            voteAnswer(answerLikeBtn, 'like');
        }

        if (answerDislikeBtn) {
            e.preventDefault();
            voteAnswer(answerDislikeBtn, 'dislike');
        }

        if (solutionBtn) {
            e.preventDefault();
            markAsSolution(solutionBtn);
        }
    });
});

function handleVote(button, voteType) {
    const questionId = button.dataset.questionId;
    if (!questionId) {
        console.error('Question ID not found');
        return;
    }

    button.disabled = true;

    fetch(`/question/${questionId}/vote/${voteType}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        credentials: 'same-origin'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            throw new Error(data.error);
        }
        updateUI(questionId, data);
        button.disabled = false;
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error: ' + error.message);
        button.disabled = false;
    });
}

function updateUI(questionId, data) {
    const ratingElement = document.querySelector(`.question-rating[data-question-id="${questionId}"]`);
    if (ratingElement) {
        ratingElement.textContent = data.rating;
    }

    const likeBtn = document.querySelector(`.like-btn[data-question-id="${questionId}"]`);
    const dislikeBtn = document.querySelector(`.dislike-btn[data-question-id="${questionId}"]`);

    if (likeBtn && dislikeBtn) {
        likeBtn.classList.remove('btn-success', 'btn-outline-success');
        dislikeBtn.classList.remove('btn-danger', 'btn-outline-danger');

        if (data.user_vote === 'like') {
            likeBtn.classList.add('btn-success');
            dislikeBtn.classList.add('btn-outline-danger');
        } else if (data.user_vote === 'dislike') {
            dislikeBtn.classList.add('btn-danger');
            likeBtn.classList.add('btn-outline-success');
        } else {
            likeBtn.classList.add('btn-outline-success');
            dislikeBtn.classList.add('btn-outline-danger');
        }
    }
}

function voteAnswer(button, voteType) {
    const answerId = button.dataset.answerId;
    const url = `/answer/${answerId}/vote/${voteType}/`;

    button.disabled = true;

    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        credentials: 'same-origin'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (typeof data.rating === 'undefined') {
            throw new Error('Rating missing in server response');
        }
        updateAnswerUI(answerId, data);
        button.disabled = false;
    })
    .catch(error => {
        console.error('Voting error:', error);
        button.disabled = false;
    });
}

function updateAnswerUI(answerId, data) {
    const likeBtn = document.querySelector(`.answer-like-btn[data-answer-id="${answerId}"]`);
    const dislikeBtn = document.querySelector(`.answer-dislike-btn[data-answer-id="${answerId}"]`);
    const ratingElement = document.querySelector(`.answer-rating[data-answer-id="${answerId}"]`);

    if (ratingElement) {
        ratingElement.textContent = data.rating;
    }

    if (likeBtn && dislikeBtn) {
        likeBtn.classList.remove('btn-success', 'btn-outline-success');
        dislikeBtn.classList.remove('btn-danger', 'btn-outline-danger');

        if (data.user_vote === 'like') {
            likeBtn.classList.add('btn-success');
            dislikeBtn.classList.add('btn-outline-danger');
        } else if (data.user_vote === 'dislike') {
            dislikeBtn.classList.add('btn-danger');
            likeBtn.classList.add('btn-outline-success');
        } else {
            likeBtn.classList.add('btn-outline-success');
            dislikeBtn.classList.add('btn-outline-danger');
        }
    }
}

function markAsSolution(button) {
    const answerId = button.dataset.answerId;
    const questionCard = document.querySelector('.question-card');
    const questionId = questionCard ? questionCard.dataset.questionId : null;

    if (!answerId || !questionId) {
        console.error('Missing IDs:', {answerId, questionId});
        showErrorNotification('Missing required information. Please try again.');
        return;
    }

    const url = `/answer/${answerId}/mark_as_solution/`;
    const originalHtml = button.innerHTML;
    button.disabled = true;
    button.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';

    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        credentials: 'same-origin'
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => {
                throw new Error(err.error || `Server returned ${response.status}`);
            }).catch(() => {
                throw new Error(`Server returned ${response.status}`);
            });
        }
        return response.json();
    })
    .then(data => {
        if (!data || typeof data.is_solution === 'undefined') {
            // Changed from is_new_solution to is_solution to match potential server response
            throw new Error('Invalid server response format');
        }
        updateSolutionUI(answerId, questionId, data.is_solution);
    })
    .catch(error => {
        console.error('Error:', error);
        showErrorNotification(error.message || 'Failed to mark as solution. Please try again.');
    })
    .finally(() => {
        button.disabled = false;
        button.innerHTML = originalHtml;
    });
}

function updateSolutionUI(answerId, questionId, isSolution) {
    try {
        document.querySelectorAll('.answer-card').forEach(card => {
            if (!card) return;

            const currentId = card.dataset.answerId;
            const solutionBtn = card.querySelector('.mark-solution-btn');
            const iconContainer = card.querySelector('.col-2.text-center');
            const existingIcon = iconContainer?.querySelector('.text-success');
            const wasSolution = solutionBtn?.dataset.wasSolution === 'true';

            if (currentId === answerId) {
                card.classList.toggle('best-answer', isSolution);

                if (isSolution) {
                    if (iconContainer && !existingIcon) {
                        const icon = document.createElement('div');
                        icon.className = 'mt-2 text-success';
                        icon.innerHTML = '<i class="bi bi-check-circle-fill"></i>';
                        iconContainer.appendChild(icon);
                    }
                    if (solutionBtn) {
                        solutionBtn.classList.replace('btn-outline-success', 'btn-success');
                        const icon = solutionBtn.querySelector('i');
                        if (icon) icon.className = 'bi bi-check-circle-fill';
                        solutionBtn.innerHTML = '<i class="bi bi-check-circle-fill"></i> Solution';
                        solutionBtn.classList.add('d-none');
                        solutionBtn.dataset.wasSolution = 'true';
                    }
                } else {
                    if (existingIcon) existingIcon.remove();
                    if (solutionBtn) {
                        solutionBtn.classList.replace('btn-success', 'btn-outline-success');
                        const icon = solutionBtn.querySelector('i');
                        if (icon) icon.className = 'bi bi-check-circle';
                        solutionBtn.innerHTML = '<i class="bi bi-check-circle"></i> Mark as solution';
                        solutionBtn.classList.remove('d-none');
                        solutionBtn.dataset.wasSolution = 'false';
                    }
                }
            } else {
                card.classList.remove('best-answer');
                if (existingIcon) existingIcon.remove();

                if (wasSolution && solutionBtn) {
                    solutionBtn.classList.replace('btn-success', 'btn-outline-success');
                    const icon = solutionBtn.querySelector('i');
                    if (icon) icon.className = 'bi bi-check-circle';
                    solutionBtn.innerHTML = '<i class="bi bi-check-circle"></i> Mark as solution';
                    solutionBtn.classList.remove('d-none');
                    solutionBtn.dataset.wasSolution = 'false';
                }

                if (solutionBtn && !wasSolution) {
                    solutionBtn.classList.remove('d-none');
                    solutionBtn.classList.replace('btn-success', 'btn-outline-success');
                }
            }
        });

        if (isSolution) {
            const container = document.querySelector('.answers-list');
            const solutionCard = document.querySelector(`.answer-card[data-answer-id="${answerId}"]`);
            if (container && solutionCard && solutionCard !== container.firstElementChild) {
                container.prepend(solutionCard);
            }
        }
    } catch (error) {
        console.error('Error in updateSolutionUI:', error);
        alert('An error occurred while updating the solution status');
    }
}