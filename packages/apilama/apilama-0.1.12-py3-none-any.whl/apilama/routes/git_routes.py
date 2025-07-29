from flask import Blueprint, jsonify, request, current_app
import os
import sys
import subprocess
import json

git_routes = Blueprint('git_routes', __name__)


def run_git_command(command, cwd=None):
    """Run a git command and return the result."""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        return {
            'status': 'success',
            'output': result.stdout.strip()
        }
    except subprocess.CalledProcessError as e:
        return {
            'status': 'error',
            'message': e.stderr.strip() or str(e)
        }


@git_routes.route('/api/git/status', methods=['GET'])
def git_status():
    """Get the git status of the markdown directory."""
    try:
        markdown_dir = os.environ.get('MARKDOWN_DIR', './markdown')
        if not os.path.exists(markdown_dir):
            return jsonify({
                'status': 'error',
                'message': 'Markdown directory does not exist'
            }), 404

        # Check if the directory is a git repository
        if not os.path.exists(os.path.join(markdown_dir, '.git')):
            return jsonify({
                'status': 'error',
                'message': 'Not a git repository'
            }), 400

        result = run_git_command(['git', 'status', '--porcelain'], cwd=markdown_dir)
        if result['status'] == 'error':
            return jsonify(result), 500

        # Parse the status output
        files = []
        for line in result['output'].split('\n'):
            if line.strip():
                status = line[:2].strip()
                filename = line[3:].strip()
                files.append({
                    'status': status,
                    'filename': filename
                })

        # Log the operation
        current_app.logger.info(f"Git status: {len(files)} files with changes")

        return jsonify({
            'status': 'success',
            'files': files
        })
    except Exception as e:
        current_app.logger.error(f"Error getting git status: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@git_routes.route('/api/git/init', methods=['POST'])
def git_init():
    """Initialize a git repository in the markdown directory."""
    try:
        markdown_dir = os.environ.get('MARKDOWN_DIR', './markdown')
        if not os.path.exists(markdown_dir):
            os.makedirs(markdown_dir, exist_ok=True)

        # Check if the directory is already a git repository
        if os.path.exists(os.path.join(markdown_dir, '.git')):
            return jsonify({
                'status': 'success',
                'message': 'Already a git repository'
            })

        result = run_git_command(['git', 'init'], cwd=markdown_dir)
        if result['status'] == 'error':
            return jsonify(result), 500

        # Log the operation
        current_app.logger.info(f"Git repository initialized in {markdown_dir}")

        return jsonify({
            'status': 'success',
            'message': 'Git repository initialized'
        })
    except Exception as e:
        current_app.logger.error(f"Error initializing git repository: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@git_routes.route('/api/git/commit', methods=['POST'])
def git_commit():
    """Commit changes in the markdown directory."""
    try:
        data = request.get_json()
        message = data.get('message', 'Update markdown files')

        markdown_dir = os.environ.get('MARKDOWN_DIR', './markdown')
        if not os.path.exists(markdown_dir):
            return jsonify({
                'status': 'error',
                'message': 'Markdown directory does not exist'
            }), 404

        # Check if the directory is a git repository
        if not os.path.exists(os.path.join(markdown_dir, '.git')):
            return jsonify({
                'status': 'error',
                'message': 'Not a git repository'
            }), 400

        # Add all changes
        add_result = run_git_command(['git', 'add', '.'], cwd=markdown_dir)
        if add_result['status'] == 'error':
            return jsonify(add_result), 500

        # Commit changes
        commit_result = run_git_command(['git', 'commit', '-m', message], cwd=markdown_dir)
        if commit_result['status'] == 'error':
            # If there's nothing to commit, that's not an error
            if 'nothing to commit' in commit_result['message']:
                return jsonify({
                    'status': 'success',
                    'message': 'Nothing to commit'
                })
            return jsonify(commit_result), 500

        # Log the operation
        current_app.logger.info(f"Git commit: {message}")

        return jsonify({
            'status': 'success',
            'message': 'Changes committed'
        })
    except Exception as e:
        current_app.logger.error(f"Error committing changes: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@git_routes.route('/api/git/log', methods=['GET'])
def git_log():
    """Get the git log of the markdown directory."""
    try:
        markdown_dir = os.environ.get('MARKDOWN_DIR', './markdown')
        if not os.path.exists(markdown_dir):
            return jsonify({
                'status': 'error',
                'message': 'Markdown directory does not exist'
            }), 404

        # Check if the directory is a git repository
        if not os.path.exists(os.path.join(markdown_dir, '.git')):
            return jsonify({
                'status': 'error',
                'message': 'Not a git repository'
            }), 400

        # Get the log in JSON format
        result = run_git_command(
            ['git', 'log', '--pretty=format:{"hash":"%h","author":"%an","date":"%ad","message":"%s"}', '--date=iso'],
            cwd=markdown_dir
        )
        if result['status'] == 'error':
            return jsonify(result), 500

        # Parse the log output
        commits = []
        for line in result['output'].split('\n'):
            if line.strip():
                try:
                    commit = json.loads(line)
                    commits.append(commit)
                except json.JSONDecodeError:
                    pass

        # Log the operation
        current_app.logger.info(f"Git log: {len(commits)} commits")

        return jsonify({
            'status': 'success',
            'commits': commits
        })
    except Exception as e:
        current_app.logger.error(f"Error getting git log: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
